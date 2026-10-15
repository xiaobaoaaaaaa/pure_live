"""Package the compiled Fedora bundle; keep private ELF capabilities private."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[2]
bundle = Path(sys.argv[1]).resolve()
meta = json.loads((root / 'packaging/fedora/release.json').read_text())

def run(args):
    return subprocess.check_output(args, text=True).strip()

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

# Prefer Fedora's libarchive instead of the Ubuntu fallback's incompatible ABI.
(bundle / 'lib/fallback/libarchive.so.13').unlink(missing_ok=True)
for rel in ['pure_live', 'lib/libmpv.so.2', 'lib/libffmpegkit.so', 'data/flutter_assets/assets/icons/icon.png']:
    assert (bundle / rel).is_file(), rel
for file in bundle.rglob('*'):
    if file.is_symlink():
        assert file.resolve().is_relative_to(bundle), file

private = set()
for file in (bundle / 'lib').rglob('*'):
    if not file.is_file():
        continue
    with file.open('rb') as stream:
        elf = stream.read(20)
    if elf[:4] != b'\x7fELF':
        continue
    assert elf[4] == 2 and int.from_bytes(elf[18:20], 'little') == 62, file
    if '.so' in file.name:
        for cap in run(['/usr/lib/rpm/rpmdeps', '--provides', str(file)]).splitlines():
            if '(' in cap:
                alias = file.name + cap[cap.index('('):]
                assert re.fullmatch(r'[A-Za-z0-9_.+()~-]+', alias), alias
                private.add(alias)
info = {
    **meta, 'fork_commit': run(['git', 'rev-parse', 'HEAD']),
    'workflow_run': os.environ.get('GITHUB_RUN_ID'),
    'platform': 'fedora-44-x86_64', 'ninja_jobs': 2,
    'runtime_tested': False, 'installation_tested': False,
    'ffmpeg_library_sha256': sha(bundle / 'lib/libffmpegkit.so'),
}
(bundle / 'rpmbridge-build.json').write_text(json.dumps(info, indent=2) + '\n')
dist = root / 'dist/fedora'
dist.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='pure-live-rpm-') as temp:
    top = Path(temp)
    for name in ['SOURCES', 'SPECS', 'BUILD', 'BUILDROOT', 'RPMS', 'SRPMS']:
        (top / name).mkdir()
    shutil.copytree(bundle, top / 'SOURCES/payload', symlinks=True)
    shutil.copy2(root / 'LICENSE', top / 'SOURCES/LICENSE')
    desktop = '[Desktop Entry]\nType=Application\nName=Pure Live\nExec=/opt/rpmbridge/pure-live/pure_live\nPath=/opt/rpmbridge/pure-live\nIcon=/opt/rpmbridge/pure-live/data/flutter_assets/assets/icons/icon.png\nTerminal=false\nCategories=AudioVideo;Player;\n'
    (top / 'SOURCES/pure-live.desktop').write_text(desktop)
    filters = '|'.join(re.escape(cap).replace('\\', '\\\\') for cap in sorted(private))
    spec = f'''%global debug_package %{{nil}}
%global __os_install_post %{{nil}}
%global _build_id_links none
%global _binary_payload w6.zstdio
%global __provides_exclude_from ^/opt/rpmbridge/pure-live/.*$
%global __requires_exclude ^({filters})$
Name: pure-live
Version: {meta['version']}
Release: {meta['release']}%{{?dist}}
Summary: Pure Live streaming desktop client
License: AGPL-3.0-only
URL: https://github.com/xiaobaoaaaaaa/pure_live
BuildArch: x86_64
Requires: gtk3, libstdc++, libarchive
%description
Pure Live with Fedora Linux window controls and verified native libraries.
%prep
%build
%install
mkdir -p %{{buildroot}}/opt/rpmbridge/pure-live
cp -a %{{_sourcedir}}/payload/. %{{buildroot}}/opt/rpmbridge/pure-live/
install -D -m 0644 %{{_sourcedir}}/pure-live.desktop %{{buildroot}}/usr/share/applications/pure-live.desktop
install -D -m 0644 %{{_sourcedir}}/LICENSE %{{buildroot}}/usr/share/licenses/pure-live/LICENSE
%files
%defattr(-,root,root,-)
/opt/rpmbridge/pure-live
/usr/share/applications/pure-live.desktop
%license /usr/share/licenses/pure-live/LICENSE
'''
    spec_path = top / 'SPECS/pure-live.spec'
    spec_path.write_text(spec)
    subprocess.run(['rpmbuild', '-bb', '--define', f'_topdir {top}', str(spec_path)], check=True)
    products = list((top / 'RPMS').rglob('*.rpm'))
    assert len(products) == 1
    rpm = products[0]
    assert run(['rpm', '-qp', '--qf', '%{NAME} %{VERSION} %{ARCH}', str(rpm)]) == f"pure-live {meta['version']} x86_64"
    subprocess.run(['rpm', '-K', '--nosignature', str(rpm)], check=True)
    requires = set(run(['rpm', '-qpR', str(rpm)]).splitlines())
    provides = set(run(['rpm', '-qp', '--provides', str(rpm)]).splitlines())
    assert not private.intersection(requires | provides)
    shutil.copy2(rpm, dist / rpm.name)
    info.update(rpm=rpm.name, rpm_sha256=sha(rpm), private_dependencies_checked=True)
(dist / 'build-info.json').write_text(json.dumps(info, indent=2) + '\n')
subprocess.run(['git', 'archive', '--format=tar.gz', f'--prefix=pure-live-{meta["version"]}/', '-o', str(dist / f'pure-live-{meta["version"]}-source.tar.gz'), 'HEAD'], check=True)
print(json.dumps(info, indent=2))
