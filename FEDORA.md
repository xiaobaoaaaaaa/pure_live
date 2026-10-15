# Pure Live for Fedora / RPMBridge

This is `xiaobaoaaaaaa/pure_live`, a Fedora packaging fork of
[`liuchuancong/pure_live`](https://github.com/liuchuancong/pure_live).
The maintained branch is `fedora`. Baseline: **3.1.18**; upstream **3.1.19** is
already available and remains a separate review/update task.

## Build and distribution

The `Fedora RPM` GitHub Actions workflow uses a digest-pinned Fedora 44 x86_64
container on a GitHub-hosted runner, Flutter 3.47.5 at a verified revision and
archive SHA-256, and the upstream dependency lockfile. Ninja uses two workers.
No private RPMBridge source, local paths, credentials or local runners are needed.

```sh
gh workflow run fedora-rpm.yml --repo xiaobaoaaaaaa/pure_live --ref fedora -f publish=false
# After a reviewed change is ready for release:
gh workflow run fedora-rpm.yml --repo xiaobaoaaaaaa/pure_live --ref fedora -f publish=true
```

A successful build produces the RPM, matching source tarball, `build-info.json`,
`SHA256SUMS` and a DNF dependency preview. Publication runs separately, after all
checks, with write access only in the publishing job. Failed builds retain the
last published release. Re-running publication never replaces existing releases.
`v<version>` in this fork identifies the **patched fork commit**, not the upstream
commit; both commit identities are recorded in build-info.json. Do not import
upstream tags into this fork's release namespace.

Only Linux is built here. This fork restores native Linux title controls, retains
the reviewed FFmpeg n9.0.2 runtime, and omits the Ubuntu libarchive fallback in
favor of Fedora's library. See the commits for the actual changes. Dependency
metadata excludes bundled libraries while preserving required system libraries.
Build success is not proof of desktop behavior or stream playback.

## Local RPMBridge

Import `packaging/fedora/rpmbridge.yaml` only after the first release is published.
It tracks this fork's stable GitHub Releases and uses the existing `upstream-rpm`
backend. Local work consists of download, SHA-256/RPM checks and artifact
registration. Installation is separate. The former source adapter can remain
installed for older recipes; Pure Live no longer requires it for new downloads.

## Maintenance

The dot's entrypoint is [DOT-HANDOFF.md](packaging/fedora/DOT-HANDOFF.md).
No dot has been assigned merely by adding these files. The owner must send the
handoff to their dot and connect GitHub. This setup does not create a local
scheduled automation or require the owner's computer to remain online.
