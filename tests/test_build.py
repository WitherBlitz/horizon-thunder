import copy
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import build

ROOT = Path(__file__).resolve().parents[1]


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.index = json.loads((ROOT / "modrinth.index.json").read_text())

    def test_pack_references_original_without_redistributing_it(self):
        with tempfile.TemporaryDirectory() as folder:
            output = build.build_pack(self.index, Path(folder))
            with zipfile.ZipFile(output) as pack:
                self.assertEqual(pack.namelist(), ["modrinth.index.json"])
                manifest = json.loads(pack.read("modrinth.index.json"))
        self.assertEqual(manifest["dependencies"], {"minecraft": "26.2"})
        self.assertEqual(len(manifest["files"]), 1)
        entry = manifest["files"][0]
        self.assertEqual(entry["path"], "mods/jjthunder-to-the-max-0.9.0.jar")
        self.assertEqual(
            entry["hashes"]["sha1"], "66b1c05891c7474567fb253a239c775e2611cca7"
        )
        self.assertEqual(len(entry["hashes"]["sha512"]), 128)
        self.assertEqual(entry["fileSize"], 176180)
        self.assertEqual(
            entry["downloads"],
            [
                (
                    "https://cdn.modrinth.com/data/1NnAVIR5/versions/IgqEqiO9/"
                    "JJThunder_To_The_Max_26.2_v0.9.0.zip"
                )
            ],
        )

    def test_build_is_reproducible_and_emits_matching_checksum(self):
        with tempfile.TemporaryDirectory() as folder:
            output = build.build_pack(self.index, Path(folder))
            first = output.read_bytes()
            self.assertEqual(
                build.build_pack(self.index, Path(folder)).read_bytes(), first
            )
            checksum = output.with_suffix(".mrpack.sha256").read_text()
            self.assertEqual(
                checksum, f"{hashlib.sha256(first).hexdigest()}  {output.name}\n"
            )

    def test_unsafe_download_paths_are_rejected(self):
        for path in (
            "../outside.jar",
            "/mods/a.jar",
            "mods/../../a.jar",
            "mods\\a.jar",
            "C:/mods/a.jar",
        ):
            with self.subTest(path=path), tempfile.TemporaryDirectory() as folder:
                index = copy.deepcopy(self.index)
                index["files"][0]["path"] = path
                with self.assertRaisesRegex(ValueError, "path"):
                    build.build_pack(index, Path(folder))

    def test_missing_hash_and_insecure_download_are_rejected(self):
        for key, value in (
            ("hashes", {}),
            ("downloads", ["http://example.com/mod.jar"]),
        ):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as folder:
                index = copy.deepcopy(self.index)
                index["files"][0][key] = value
                with self.assertRaises(ValueError):
                    build.build_pack(index, Path(folder))


if __name__ == "__main__":
    unittest.main()
