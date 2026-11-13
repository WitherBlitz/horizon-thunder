"""Build a reproducible Horizon-importable pack without bundling upstream data."""

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent


def build_pack(index: dict, output_dir: Path) -> Path:
    """Validate the download manifest and emit a deterministic .mrpack + SHA-256."""
    version = index.get("versionId", "")
    if not isinstance(version, str) or not re.fullmatch(
        r"[0-9]+\.[0-9]+\.[0-9]+", version
    ):
        raise ValueError("versionId must be a numeric major.minor.patch version")
    if index.get("formatVersion") != 1 or index.get("game") != "minecraft":
        raise ValueError("Expected Minecraft mrpack formatVersion 1")
    if not index.get("dependencies", {}).get("minecraft") or not index.get("files"):
        raise ValueError("A Minecraft version and at least one download are required")
    paths = set()
    for entry in index["files"]:
        path = entry.get("path", "")
        parts = PurePosixPath(path).parts
        if (
            not parts
            or parts[0] != "mods"
            or len(parts) < 2
            or ".." in parts
            or "\\" in path
            or ":" in path
            or path in paths
        ):
            raise ValueError(f"Invalid or duplicate mod path: {path}")
        paths.add(path)
        for algorithm, length in (("sha1", 40), ("sha512", 128)):
            digest = entry.get("hashes", {}).get(algorithm, "")
            if not isinstance(digest, str) or not re.fullmatch(
                f"[0-9a-f]{{{length}}}", digest
            ):
                raise ValueError(f"{path}: a pinned {algorithm} is required")
        urls = entry.get("downloads", [])
        if not urls or any(
            urlparse(url).scheme != "https" or not urlparse(url).netloc for url in urls
        ):
            raise ValueError(f"{path}: HTTPS downloads are required")
        if not isinstance(entry.get("fileSize"), int) or entry["fileSize"] <= 0:
            raise ValueError(f"{path}: a positive fileSize is required")
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"horizon-thunder-{version}.mrpack"
    info = zipfile.ZipInfo("modrinth.index.json", date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    manifest = json.dumps(index, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    with zipfile.ZipFile(output, "w") as pack:
        pack.writestr(info, manifest)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(".mrpack.sha256").write_text(
        f"{digest}  {output.name}\n", encoding="utf-8", newline="\n"
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    index = json.loads((ROOT / "modrinth.index.json").read_text(encoding="utf-8"))
    print(build_pack(index, args.output))


if __name__ == "__main__":
    main()
