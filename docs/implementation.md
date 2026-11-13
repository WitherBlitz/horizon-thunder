# Horizon Thunder

## Design

An extensible personal Horizon modpack, starting with JJThunder To The Max
0.9.0 for Minecraft 26.2. The installable artifact is a Modrinth `.mrpack`:
Horizon imports it into its own profile and upgrades the data-only archive
to 26.3 using its existing converter. No Java code or mod loader is needed.
The source version stays 26.2 in the manifest so Horizon selects the converter.

The pack references the official Modrinth CDN file and pins its SHA-1,
SHA-512 and size. It does not redistribute JJThunder's All Rights Reserved
data. Using a custom Rust terrain generator would duplicate Horizon's
converter and make terrain fidelity harder to maintain. A native `.hpack`
requires registry-listed mods and is unnecessary for this data-only pack.

Acceptance: a reproducible `.mrpack`; the official launcher imports and
ports it into a separate profile; new worlds receive the converted data;
GitHub builds/releases the artifact; runtime verification is reported
separately from conversion success. Existing worlds are never modified.

## Implementation plan

- [x] Add the pinned pack index and tests for artifact structure, upstream
  integrity metadata, reproducibility and invalid paths.
- [x] Add a dependency-free builder; run the narrow and full test suites.
- [x] Exercise the official Horizon launcher import/port path in isolated
  scratch homes. Inspect conversion notes and generated settings.
- [x] Add usage instructions and CI/release automation. Publish to the
  user's selected GitHub account after verifying the final artifact.
- [x] Check the installed launcher/game and generate a fresh test world
  when its location is available; disclose remaining compatibility gaps.

## Verification commands

Install: no third-party Python packages required (Python 3.11+).
Build: `python build.py`.
Narrow tests: `python -m unittest tests.test_build -v`.
Full suite: `python -m unittest discover -s tests -v`.
Lint/format: `ruff check .` and `ruff format --check .` (development tool).
Integration: isolated `horizon-launcher modpack import`, `modpack port`,
and inspection of the resulting profile and converter report.
