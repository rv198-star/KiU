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


if __name__ == "__main__":
    unittest.main()
