# Horizon Thunder

A personal, expandable modpack for [Horizon](https://github.com/horizon-rust/horizon),
starting with **JJThunder To The Max 0.9.0** by jjthunder001.

**Use the current Horizon Nightly.** Tested with launcher **0.2.63** and game
**nightly-2026-11-13-9f42064** on Windows. The old `v0.2.97` release is marked
outdated by Horizon. This pack is a first release, with runtime smoke testing;
full terrain parity against Java Minecraft has not been established.

## Install

1. Download `horizon-thunder-0.1.0.mrpack` from the
   [latest GitHub release](https://github.com/WitherBlitz/horizon-thunder/releases/latest).
2. In Horizon Launcher, open **Modpacks** and import the downloaded file.
   Click **Port 1 mods** and wait for it to finish. The result should show
   **1 data pack for new worlds** before you play.
3. Play **Horizon Thunder** using the current **Nightly**, then create a **new world**.

The pack has its own saves and settings. JJThunder is automatically enabled
in each new world in this profile. Do not add it to an existing world or
combine it with other terrain generators.

The command-line equivalent, using your launcher executable, is:

```powershell
.\horizon-launcher.exe modpack import .\horizon-thunder-0.1.0.mrpack
.\horizon-launcher.exe modpack port horizon-thunder
.\horizon-launcher.exe instance version port:horizon-thunder nightly-2026-11-13-9f42064
.\horizon-launcher.exe modpack play horizon-thunder --version nightly-2026-11-13-9f42064
```

Use the version tag of your installed Nightly if it differs. Imports need
internet access to download the original pack from Modrinth. If the launcher
reports no data packs or refuses the converted worldgen, update the launcher
and game to the current Nightly rather than continuing in an unmodified world.

## How the port works

JJThunder's terrain is data, so it does not require a Java runtime or a
new Rust terrain implementation. This manifest references its official
Minecraft 26.2 download. Horizon's existing converter rewrites its density
functions, noise settings, biomes and surface rules for Minecraft 26.3.
The converted data goes into the profile's `new-world-datapacks/` directory.

The `.jar` destination in the manifest is intentional: a data-only JAR and
the original data-pack ZIP are both ZIP archives. Horizon recognizes the
`pack.mcmeta`, worldgen data and absence of Java classes, then installs it
as a data pack. No Fabric or Forge loader is requested. The manifest's
Minecraft version must remain **26.2** for this conversion to run.

JJThunder is **All Rights Reserved**. This repository and its releases contain
only our manifest and tooling; the original and converted JJThunder files
are never included. Downloads are pinned by SHA-1, SHA-512 and size. Original
project: [JJThunder To The Max on Modrinth](https://modrinth.com/datapack/jjthunder-to-the-max).
This project is unofficial and is not endorsed by JJThunder, Horizon or Mojang.

## Add mods or publish an update

Edit `modrinth.index.json`: add official downloads with their hashes and size,
and bump `versionId`. Horizon still needs to support each added mod's behavior;
ordinary Java mod code does not run automatically. Keep competing worldgen
mods out of this pack.

Python 3.11+ is required to build; no runtime packages are needed:

```powershell
python build.py
python -m unittest discover -s tests -v
```

For lint and the optional live upstream integrity check:

```powershell
python -m pip install ruff==0.17.5
python -m ruff check .
python -m ruff format --check .
$env:HORIZON_VERIFY_DOWNLOADS = '1'
python -m unittest discover -s tests -v
```

CI runs these checks and builds the `.mrpack` and its SHA-256 checksum.
Pushing a tag matching the manifest version, such as `v0.1.0`, publishes
those artifacts to a GitHub release. `RELEASE_NOTES.md` supplies its notes.

Windows runtime verification is available in `tools/verify_horizon.py`.
Point `--game-root` at an installed Nightly, `--profile` at an isolated
imported pack profile, and `--scratch` at a fresh scratch directory. It creates
a test world, waits for terrain, checks chunk decoding and building at Y=1000,
saves a screenshot and exits. Use only scratch profiles for this test.

See [verification.md](docs/verification.md) for the first release's results.
