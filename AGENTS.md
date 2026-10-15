# Fedora fork maintenance

This fork maintains Fedora x86_64 RPMs of Pure Live for RPMBridge. The owner's
current request takes precedence. This file governs the `fedora` branch;
upstream guidance is retained as `packaging/fedora/UPSTREAM-AGENTS.md` for context.
Do not run upstream Android/Windows release, signing or deployment workflows.

- Read `FEDORA.md` and `packaging/fedora/DOT-HANDOFF.md` first.
- Use GitHub-hosted CI for heavy builds; never require the owner's local machine.
- Preserve Linux window controls, the native-assets install rules, system
  libarchive preference and the FFmpeg hash/ELF checks.
- Keep fork changes as small commits. Preserve upstream licenses and source.
- Never automatically merge an unreviewed upstream release or merely bypass a
  version, dependency lockfile, checksum or test failure.
- Review upstream changes on a separate branch, update release.json deliberately,
  run affected tests, then build with the Fedora RPM workflow. Keep build logs
  and report failures. Do not claim runtime/playback acceptance from compilation.
- Do not force-push, move published tags, replace published assets or expose tokens.
- Upstream release tags and fork release tags have separate provenance. Fetch
  upstream tags into `refs/remotes/upstream/releases/`, not local release tags.
- Dots activation/monitoring must be explicitly confirmed in the dot conversation.
  These repository files are instructions, not proof that a dot is running.
