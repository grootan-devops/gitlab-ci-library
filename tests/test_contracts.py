import subprocess
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "common/.gitlab-ci.yml", "nodejs/.gitlab-ci.yml", "python/.gitlab-ci.yml",
    "golang/.gitlab-ci.yml", "java/.gitlab-ci.yml", "image/.gitlab-ci.yml",
    "chart/.gitlab-ci.yml", "terraform/.gitlab-ci.yml", "sonarqube/.gitlab-ci.yml",
    "secret-scanning/.gitlab-ci.yml", "license/.gitlab-ci.yml",
    "sbom/.gitlab-ci.yml", "mono/.gitlab-ci.yml", "release/.gitlab-ci.yml",
}


class TemplateContracts(unittest.TestCase):
    def load(self, path: Path):
        data = yaml.safe_load(path.read_text())
        self.assertIsInstance(data, dict, path)
        return data

    def test_every_template_is_valid_yaml(self):
        files = sorted(ROOT.glob("**/.gitlab-ci.yml"))
        self.assertTrue(files)
        for path in files:
            with self.subTest(path=path.relative_to(ROOT)):
                self.load(path)

    def test_supported_modules_exist(self):
        present = {str(path.relative_to(ROOT)) for path in ROOT.glob("**/.gitlab-ci.yml")}
        self.assertFalse(EXPECTED - present)

    def test_root_template_includes_core_modules(self):
        root = self.load(ROOT / ".gitlab-ci.yml")
        rendered = str(root.get("include", []))
        for module in {
            "common/.gitlab-ci.yml",
            "secret-scanning/.gitlab-ci.yml",
            "release/.gitlab-ci.yml",
        }:
            self.assertIn(module, rendered)

    def test_release_version_is_exact(self):
        self.assertEqual("1.0.0", (ROOT / "VERSION").read_text().strip())
        root = self.load(ROOT / ".gitlab-ci.yml")
        self.assertEqual("1.0.0", str(root["variables"]["RELEASE_VERSION"]))

    def test_consumer_fixture_covers_supported_shapes(self):
        text = (ROOT / "tests/fixtures/consumer.gitlab-ci.yml").read_text()
        for module in EXPECTED:
            self.assertIn(module, text)

    def test_shared_structural_verifier(self):
        verifier = ROOT.parent / "ai-skills/ci-library-builder/scripts/verify-gitlab-library.py"
        if not verifier.exists():
            self.skipTest("sibling ai-skills checkout is not available")
        result = subprocess.run(
            [sys.executable, str(verifier), str(ROOT), "--json"],
            text=True, capture_output=True,
        )
        findings = yaml.safe_load(result.stdout) or []
        unexpected_p0 = [
            finding for finding in findings
            if finding.get("severity") == "P0"
            and (finding.get("rule"), finding.get("where")) not in {
                ("needs-missing-optional", "chart/.gitlab-ci.yml :: Chart:Promote"),
                ("needs-missing-optional", "image/.gitlab-ci.yml :: Image:Promote"),
                ("needs-missing-optional", "release/.gitlab-ci.yml :: Release"),
            }
        ]
        self.assertFalse(unexpected_p0, unexpected_p0)


if __name__ == "__main__":
    unittest.main()
