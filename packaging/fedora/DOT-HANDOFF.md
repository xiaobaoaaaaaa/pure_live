# Dots maintenance assignment

Repository: https://github.com/xiaobaoaaaaaa/pure_live
Maintained branch: `fedora`
Upstream: https://github.com/liuchuancong/pure_live
Build workflow: `.github/workflows/fedora-rpm.yml`

## Owner's intended responsibility

Maintain this fork's Fedora x86_64 RPMs in the cloud. Track upstream stable
releases, review and integrate compatible updates, preserve the Fedora fixes,
repair build failures and publish validated releases. Keep RPMBridge's local
client download-only. Use this repository, PRs, CI logs and Releases as the
shared state with local Codex; no direct Codex-to-dot API is required.

## First run

1. Read AGENTS.md, FEDORA.md, packaging/fedora/release.json and recent commits.
2. Confirm GitHub repository read/write access and ability to dispatch Actions.
   If missing, ask the owner to connect the required account; never request a token
   in chat. Confirm to the owner that you have accepted the ongoing assignment.
3. Inspect the latest Fedora RPM workflow and release. Do not call a draft,
   failed run or uploaded artifact a published working release.
4. The baseline is 3.1.18. Upstream 3.1.19 was observed on 2026-10-15; review it as
   the first update after baseline cloud publication is verified.
5. Arrange follow-ups using your own supported cloud task controls. Stay quiet
   while nothing actionable changes. Notify on a successful new release,
   persistent failure, patch conflict or decision requiring the owner.

## Update procedure

- Fetch the specific upstream tag into a separate ref, for example:
  `git fetch upstream refs/tags/v3.1.19:refs/remotes/upstream/releases/v3.1.19`.
- Create an update branch from `fedora`; compare upstream commits and review the
  affected desktop, native library, SDK, build scripts and dependency changes.
- Integrate changes while preserving Linux title controls, FFmpeg verification,
  CMake native-assets staging and Fedora libarchive handling. Keep upstream code
  and downstream fixes recognizable. Do not re-enable upstream multi-platform CI.
- Update release.json with the exact upstream commit/version, verified SDK and
  lockfile hash. Update setup/workflow SDK pins together if a reviewed SDK change
  is required. Do not change pins just to hide a failing check.
- Run `python3 packaging/fedora/verify.py`, affected tests, `git diff --check`,
  and the Fedora CI build. Submit a PR containing changes and evidence. Merge
  only after checks and the applicable owner authorization permit it.
- Dispatch publication from `fedora` with `publish=true`. Check the release tag
  points at the built fork commit, digests match, and the RPM version/architecture
  are correct. Preserve old releases and the last working download on failure.
- Published releases are immutable. Same-upstream-version rebuilds need an
  explicitly reviewed versioning/download-policy change; do not overwrite assets.

## Limits and reporting

The CI runner is the build host. Do not route compilation to the owner's laptop.
No automated install on the owner's machine. Separate build, dependency preview,
publication and runtime/playback evidence. The owner controls any new credentials,
paid runner capacity or repository-visibility changes. Do not report ongoing
maintenance as active until you have actually accepted and configured it.
