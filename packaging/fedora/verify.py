"""Check the Fedora patch contract before dependency resolution or compilation."""
import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[2]
release = json.loads((root / 'packaging/fedora/release.json').read_text())
assert re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', release['version'])
assert re.fullmatch(r'[1-9][0-9]*', release['release'])
assert release['upstream_tag'] == 'v' + release['version']
assert re.fullmatch(r'[a-f0-9]{40}', release['upstream_commit'])
assert json.loads((root / '.fvmrc').read_text())['flutter'] == release['flutter_version']
assert hashlib.sha256((root / 'pubspec.lock').read_bytes()).hexdigest() == release['pubspec_lock_sha256']
pubspec = (root / 'pubspec.yaml').read_text(encoding='utf-8-sig')
assert re.search(r'^version:\s*' + re.escape(release['version']) + r'\+', pubspec, re.M)
assert 'linux: https://github.com/wzgrx/pure_live/releases/download/native-ffmpeg-9.0.2-b1/bundle-base-linux-x86_64-shared-lgpl.zip' in pubspec
assert 'Platform.isLinux ? TitleBarStyle.normal : TitleBarStyle.hidden' in (root / 'lib/core/platform/desktop_manager.dart').read_text()
assert 'gtk_header_bar_set_decoration_layout(header_bar, ":minimize,maximize,close")' in (root / 'linux/my_application.cc').read_text()
assert 'native_assets/linux/' in (root / 'linux/CMakeLists.txt').read_text()
package = (root / 'packaging/fedora/package.py').read_text()
assert "(bundle / 'lib/fallback/libarchive.so.13').unlink(missing_ok=True)" in package
assert 'Requires: gtk3, libstdc++, libarchive' in package
build = (root / 'packaging/fedora/build.sh').read_text()
assert 'python3 tool/verify_ffmpeg_native.py linux "$bundle" --stage-linux' in build
print('Fedora source, version, SDK, lockfile and native-library contract verified.')
