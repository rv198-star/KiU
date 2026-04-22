import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PackagingMetadataTests(unittest.TestCase):
    def test_pyproject_declares_pyyaml_dependency(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        dependencies = pyproject["project"].get("dependencies", [])

        self.assertTrue(
            any(dep.lower().startswith("pyyaml") for dep in dependencies),
            "pyproject.toml must declare PyYAML so a clean install can run validator and pipeline commands.",
        )

    def test_pyproject_version_is_not_behind_latest_changelog_release(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        version = pyproject["project"]["version"]
        releases = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", changelog, flags=re.MULTILINE)

        self.assertTrue(releases, "CHANGELOG.md must contain at least one released version section.")
        latest_release = releases[0]
        self.assertGreaterEqual(
            tuple(int(part) for part in version.split(".")),
            tuple(int(part) for part in latest_release.split(".")),
            "pyproject.toml version must not lag behind the latest released version recorded in CHANGELOG.md.",
        )

    def test_changelog_records_v042_release(self) -> None:
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIsNotNone(
            re.search(r"^## \[0\.4\.2\] - ", changelog, flags=re.MULTILINE),
            "CHANGELOG.md must record the v0.4.2 release section.",
        )


if __name__ == "__main__":
    unittest.main()
