# Pure Live for Fedora / RPMBridge

This is `xiaobaoaaaaaa/pure_live`, a Fedora packaging fork of
[`liuchuancong/pure_live`](https://github.com/liuchuancong/pure_live).
The maintained branch is `fedora`. The latest verified published RPM is
[**3.1.19-1**](https://github.com/xiaobaoaaaaaa/pure_live/releases/tag/v3.1.19),
published on **2026-10-15**. The earlier **3.1.18-6** baseline remains available
unchanged.

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

A PR that changes `packaging/fedora/release.json`, the release gate, or the
Fedora workflow schedules a fresh build and publication when merged into
`fedora`. Gate/workflow repair PRs can retry an unpublished release without
dummy version changes; an existing release still stops publication unchanged.
A read-only gate first verifies that the push commit is the PR's merge commit
and that the exact PR head passed the
`Fedora RPM` pull-request workflow. Direct pushes and stale/failed checks do not
qualify. GitHub may clear the run's PR association after merge; in that case the
gate additionally requires an exact PR-head SHA, branch and source-repository
identity match. The manual commands above remain available. The gated
publication path was verified by its first successful end-to-end run on
**2026-10-15**; see the release evidence below.

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

The owner assigned ongoing cloud maintenance on **2026-10-15**, and daily
stable-release checks are configured. The entrypoint remains
[DOT-HANDOFF.md](packaging/fedora/DOT-HANDOFF.md). The first update to
**3.1.19-1** is complete. Subsequent stable upstream releases follow the same
review, exact-head CI, merge, fresh cloud build and publication checks. PRs,
Actions logs and Releases are the shared maintenance record. No local scheduled
task or online owner computer is required. Runtime and live playback acceptance
remain separate from the cloud build checks.

## Verified release evidence

- Release: [v3.1.19](https://github.com/xiaobaoaaaaaa/pure_live/releases/tag/v3.1.19),
  published stable on **2026-10-15**; RPM `pure-live-3.1.19-1.fc44.x86_64.rpm`.
- Source/tag commit: [`00ac3d01e6b892668aea653952a989c59ae0fb82`](https://github.com/xiaobaoaaaaaa/pure_live/commit/00ac3d01e6b892668aea653952a989c59ae0fb82).
- Successful [gate, build and publication run 38761956650](https://github.com/xiaobaoaaaaaa/pure_live/actions/runs/38761956650):
  **116 Flutter tests and 22 Python tests passed**, with FFmpeg verification,
  RPM identity/digest checks and the DNF dependency preview completed.
- Reviewed changes: [upstream update PR #1](https://github.com/xiaobaoaaaaaa/pure_live/pull/1)
  and [merged-PR provenance repair PR #2](https://github.com/xiaobaoaaaaaa/pure_live/pull/2).
- Release tag, asset digests, build-info provenance and SHA256SUMS were verified;
  earlier v3.1.18 assets remain unchanged. Published releases are not overwritten.
- Desktop behavior, local installation and live playback remain **unverified**.
