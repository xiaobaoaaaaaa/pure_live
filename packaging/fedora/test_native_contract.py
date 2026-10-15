"""Offline regression tests for the preserved Linux FFmpeg verification gates.

Synthetic archives exercise verifier behavior without downloading or executing
native code. Only each test's archive digest is substituted; the production pin
is checked independently and is never changed by these tests.
"""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('verify_ffmpeg_native', ROOT / 'tool/verify_ffmpeg_native.py')
native = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(native)


def library(*, machine=62, glibc=b'2.39', version=b'n9.0.2'):
    header = bytearray(20)
    header[:5] = b'\x7fELF\x02'
    header[18:20] = machine.to_bytes(2, 'little')
    return bytes(header) + version + b'\0GLIBC_' + glibc + b'\0'


class LinuxNativeContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = self.root / 'bundle'
        self.bundle.mkdir()
        self.archive = self.root / native.ARCHIVES['linux'][0]

    def archive_with(self, payload):
        with zipfile.ZipFile(self.archive, 'w') as archive:
            archive.writestr(native.LINUX_LIBRARY_ENTRY, payload)
        digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        return patch.dict(native.ARCHIVES, linux=(self.archive.name, digest))

    def test_reviewed_production_archive_pin_is_unchanged(self):
        self.assertEqual(native.ARCHIVES['linux'], (
            'bundle-base-linux-x86_64-shared-lgpl.zip',
            'd6003c3feb2bdcdccd0d4ad5e7b76fa8e8951430c6a22c1db7be5e13da19403d',
        ))

    def test_staged_library_matches_verified_archive(self):
        payload = library()
        with self.archive_with(payload):
            target = native.stage_linux_runtime(self.bundle, self.archive)
            self.assertEqual(target.read_bytes(), payload)
            result = native.verify('linux', self.bundle, self.archive)
        self.assertEqual(result['library_sha256'], hashlib.sha256(payload).hexdigest())

    def test_tampered_archive_is_rejected_before_staging(self):
        with self.archive_with(library()):
            self.archive.write_bytes(self.archive.read_bytes() + b'tampered')
            with self.assertRaisesRegex(ValueError, 'SHA-256 differs'):
                native.stage_linux_runtime(self.bundle, self.archive)
        self.assertFalse((self.bundle / 'lib/libffmpegkit.so').exists())

    def test_non_x86_64_elf_is_rejected(self):
        with self.archive_with(library(machine=183)):
            native.stage_linux_runtime(self.bundle, self.archive)
            with self.assertRaisesRegex(ValueError, 'not an x86_64 ELF'):
                native.verify('linux', self.bundle, self.archive)

    def test_newer_glibc_requirement_is_rejected(self):
        with self.archive_with(library(glibc=b'2.40')):
            native.stage_linux_runtime(self.bundle, self.archive)
            with self.assertRaisesRegex(ValueError, 'glibc baseline'):
                native.verify('linux', self.bundle, self.archive)

    def test_wrong_ffmpeg_version_is_rejected(self):
        with self.archive_with(library(version=b'n8.0.0')):
            native.stage_linux_runtime(self.bundle, self.archive)
            with self.assertRaisesRegex(ValueError, 'does not contain n9.0.2'):
                native.verify('linux', self.bundle, self.archive)

    def test_duplicate_packaged_library_is_rejected(self):
        with self.archive_with(library()):
            target = native.stage_linux_runtime(self.bundle, self.archive)
            duplicate = self.bundle / 'other/libffmpegkit.so'
            duplicate.parent.mkdir()
            duplicate.write_bytes(target.read_bytes())
            with self.assertRaisesRegex(ValueError, 'Expected one packaged Linux FFmpeg library'):
                native.verify('linux', self.bundle, self.archive)


if __name__ == '__main__':
    unittest.main()
