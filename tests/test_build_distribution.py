import importlib.util
import io
import json
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_distribution", ROOT / "scripts" / "build_distribution.py"
)
assert SPEC and SPEC.loader
BUILD_DISTRIBUTION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD_DISTRIBUTION)


class TraeReleasePackageTest(unittest.TestCase):
    def test_multi_skill_plugin_becomes_bundle_of_uploadable_zips(self):
        plugin = {"id": "engineering", "version": "0.1.0"}
        skill_archives = {
            "review": b"review-zip",
            "verify": b"verify-zip",
        }

        payload = BUILD_DISTRIBUTION.build_trae_release_package(
            plugin, skill_archives
        )

        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            self.assertEqual(
                sorted(archive.namelist()),
                ["MANIFEST.json", "README.md", "review.zip", "verify.zip"],
            )
            manifest = json.loads(archive.read("MANIFEST.json"))
            self.assertEqual(manifest["name"], "engineering")
            self.assertEqual(manifest["version"], "0.1.0")
            self.assertEqual(manifest["upload"], "extract-and-upload-each-zip")
            self.assertEqual(manifest["skills"], ["review", "verify"])

    def test_single_skill_plugin_remains_directly_uploadable(self):
        plugin = {"id": "baoyu-design", "version": "0.1.0"}
        direct_upload = b"direct-upload-zip"

        payload = BUILD_DISTRIBUTION.build_trae_release_package(
            plugin, {"baoyu-design": direct_upload}
        )

        self.assertEqual(payload, direct_upload)


if __name__ == "__main__":
    unittest.main()
