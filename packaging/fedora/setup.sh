#!/usr/bin/env bash
set -euo pipefail
dnf -y install git curl tar xz unzip zip python3 python3-pyyaml rpm-build \
  clang cmake ninja-build gcc-c++ pkgconf-pkg-config gtk3-devel \
  libayatana-appindicator-gtk3-devel libsecret-devel libepoxy-devel \
  libX11-devel libXrandr-devel libXinerama-devel libXcursor-devel libXi-devel \
  libXext-devel libXtst-devel libXfixes-devel alsa-lib-devel libarchive \
  mesa-libEGL-devel mesa-libGL-devel util-linux findutils which
python3 packaging/fedora/verify.py
if ! test -x /opt/flutter/bin/flutter; then
  curl --fail --location --retry 3 \
    https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.47.5-stable.tar.xz \
    --output /tmp/flutter.tar.xz
  printf '%s  /tmp/flutter.tar.xz\n' 2132e990f236f8d22e7c6314b29a191a95b10d7cbcfec9b4e2e303d996652cbb | sha256sum --check
  tar -xJf /tmp/flutter.tar.xz -C /opt
  rm /tmp/flutter.tar.xz
fi
id builder >/dev/null 2>&1 || useradd --create-home builder
mkdir -p /opt/pub-cache
chown -R builder:builder /opt/flutter /opt/pub-cache "$PWD"
runuser -u builder -- env HOME=/home/builder PUB_CACHE=/opt/pub-cache \
  FLUTTER_ROOT=/opt/flutter CI=true FLUTTER_SUPPRESS_ANALYTICS=true \
  bash packaging/fedora/build.sh
