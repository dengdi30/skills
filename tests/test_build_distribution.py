import importlib.util
import io
import json
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


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


class VendoredProvenanceTest(unittest.TestCase):
    def test_multi_skill_plugin_preserves_each_skills_provenance(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            plugin = {
                "id": "interview",
                "display_name": "Interview",
                "description": "Interview skills",
                "long_description": "Interview entry point and shared rules",
                "version": "1.0.0",
                "category": "Developer Tools",
                "default_prompt": "Interview me",
                "license_file": "LICENSE.txt",
                "provenance_files": {},
                "skills": [],
            }
            records = {}
            (root / "LICENSE.txt").write_text("Fixture license\n")
            for name in ("interview", "questions"):
                source = root / "third-party" / name
                source.mkdir(parents=True)
                (source / "SKILL.md").write_text(
                    f"---\nname: {name}\ndescription: Fixture\n---\n\n{name}\n"
                )
                record = {"path": f"upstream/{name}", "commit": "a" * 40}
                records[name] = record
                provenance_path = f"third-party/{name}.upstream.json"
                (root / provenance_path).write_text(json.dumps(record))
                plugin["skills"].append(f"third-party/{name}")
                plugin["provenance_files"][name] = provenance_path
            catalog_path = root / "catalog.json"
            catalog_path.write_text(json.dumps({
                "schema_version": 1,
                "marketplace": {
                    "name": "fixture", "display_name": "Fixture", "owner": "Fixture"
                },
                "plugins": [plugin],
            }))

            with patch.multiple(BUILD_DISTRIBUTION, ROOT=root, CATALOG_PATH=catalog_path):
                with redirect_stdout(io.StringIO()):
                    BUILD_DISTRIBUTION.build(check=False)
                    BUILD_DISTRIBUTION.build(check=True)

            self.assertEqual(
                json.loads((root / "plugins/interview/UPSTREAM.json").read_text()),
                {"skills": records},
            )
            with zipfile.ZipFile(root / "dist/trae/interview-1.0.0.zip") as bundle:
                for name, record in records.items():
                    with zipfile.ZipFile(io.BytesIO(bundle.read(f"{name}.zip"))) as skill:
                        self.assertEqual(json.loads(skill.read("UPSTREAM.json")), record)
                        self.assertEqual(skill.read("LICENSE.txt"), b"Fixture license\n")


if __name__ == "__main__":
    unittest.main()
