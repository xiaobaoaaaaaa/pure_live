#!/usr/bin/env bash
set -euo pipefail
export PATH="$FLUTTER_ROOT/bin:$PATH"
python3 packaging/fedora/verify.py
python3 -m unittest discover -s packaging/fedora -p 'test_*.py' -v
actual_revision=$(git -C "$FLUTTER_ROOT" rev-parse HEAD)
expected_revision=$(python3 -c 'import json;print(json.load(open("packaging/fedora/release.json"))["flutter_revision"])')
test "$actual_revision" = "$expected_revision"
flutter --version
version=$(python3 -c 'import json;print(json.load(open("packaging/fedora/release.json"))["version"])')
mkdir -p .fedora-bin
printf '#!/bin/sh\nexec /usr/bin/ninja -j2 "$@"\n' > .fedora-bin/ninja
chmod +x .fedora-bin/ninja
export PATH="$PWD/.fedora-bin:$PATH"
export CMAKE_BUILD_PARALLEL_LEVEL=2
flutter pub get --enforce-lockfile
python3 packaging/fedora/verify.py
dart run enven --env-files .env,.env.prod --class-name AppConfig
# Offline regression coverage; live network probes remain opt-in.
flutter test --no-pub test/core/player test/domains/live \
  test/shared/platforms/huya_headline_panel_test.dart
flutter build linux --release --no-pub --build-name="$version" --dart-define=PURELIVE_BUILD_SOURCE=fedora-fork
bundle=build/linux/x64/release/bundle
python3 tool/verify_ffmpeg_native.py linux "$bundle" --stage-linux
python3 packaging/fedora/package.py "$bundle"
# Resolve dependencies inside the same Fedora release without installing the app.
dnf --assumeno install dist/fedora/*.rpm > dist/fedora/dnf-preview.txt 2>&1 || true
python3 - <<'PY'
from pathlib import Path
text=Path('dist/fedora/dnf-preview.txt').read_text()
if 'Transaction Summary' not in text or 'nothing provides' in text:
    raise SystemExit('DNF dependency resolution failed:\n'+text)
PY
(cd dist/fedora && sha256sum -- *.rpm *.tar.gz build-info.json > SHA256SUMS)
