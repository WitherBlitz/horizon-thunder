"""Opt-in network check that the official download still matches the lock."""

import hashlib
import json
import os
import unittest
from pathlib import Path
from urllib.request import Request, urlopen


@unittest.skipUnless(
    os.environ.get("HORIZON_VERIFY_DOWNLOADS") == "1", "opt-in network test"
)
class UpstreamTests(unittest.TestCase):
    def test_official_jjthunder_download_matches_both_hashes_and_size(self):
        index = json.loads(
            (Path(__file__).resolve().parents[1] / "modrinth.index.json").read_text()
        )
        for entry in index["files"]:
            request = Request(
                entry["downloads"][0],
                headers={"User-Agent": "WitherBlitz/horizon-thunder verification"},
            )
            with urlopen(request, timeout=30) as response:
                data = response.read(entry["fileSize"] + 1)
            self.assertEqual(len(data), entry["fileSize"])
            for algorithm, expected in entry["hashes"].items():
                self.assertEqual(hashlib.new(algorithm, data).hexdigest(), expected)
