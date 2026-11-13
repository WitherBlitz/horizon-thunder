# Verification: 0.1.0

Test date: 2026-11-13. Platform: Windows x64.
Launcher: 0.2.63. Game: installed Nightly 2026-11-13, commit `9f42064`.

The official launcher imported `horizon-thunder-0.1.0.mrpack` in isolated
`HORIZON_HOME` and `HORIZON_LAUNCHER_HOME` directories, fetched the official
JJThunder archive and classified it as content/data with zero Java classes.
`modpack port horizon-thunder` returned exit 0, **1 data pack for new worlds**,
and **0 conversion notes**. The generic coverage table labels this `partial`;
that label is not a claim of complete Java parity.

The converted `pack.mcmeta` has pack format 121. Its dimension and noise
settings both retain `min_y = -64`, `height = 2096` (through Y=2031).

`tools/verify_horizon.py` ran the installed Nightly offscreen using that
profile's new-world data packs. In a fresh seed-42 world it observed:

- 49 loaded chunks, 0 pending chunks, 0 chunk decode errors.
- 181 non-air blocks in the sampled spawn column.
- Successful placement and reading of a gold block at Y=1000; the marker
  was removed afterwards.
- A rendered terrain screenshot, saved world, and clean game exit.

Packaging tests cover a reference-only archive, reproducibility, checksum,
unsafe paths, missing integrity metadata and insecure URLs. An opt-in network
test verifies the actual upstream bytes against both hashes and size.

Limits: this is a smoke test of import, conversion, new-world loading and
extended height. It does not compare JJThunder terrain against Java block
for block, measure performance at large render distances, or establish
multiplayer compatibility. Other Horizon versions have not been validated.
The old stable v0.2.97 was not certified: it predates the current test CLI
and is marked outdated by the upstream release notes.
