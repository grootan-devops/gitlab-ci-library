"""Regression checks for GitLab helper shapes and Runner shell startup."""

from pathlib import Path
import shutil
import subprocess
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]


def flatten(value):
    if isinstance(value, str):
        return [value]
    if not isinstance(value, list):
        raise AssertionError(f"Invalid script type: {type(value).__name__}")
    return [line for item in value for line in flatten(item)]


class RuntimeTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = yaml.safe_load((ROOT / "chart/.gitlab-ci.yml").read_text())
        cls.python = yaml.safe_load((ROOT / "python/.gitlab-ci.yml").read_text())

    def test_chart_helpers_are_hidden_job_mappings(self):
        for name in (".chart-registry", ".chart-login", ".chart-dependency-update"):
            with self.subTest(name=name):
                self.assertIsInstance(self.chart[name], dict)
                self.assertTrue(flatten(self.chart[name]["script"]))

    def test_registry_aliases_preserve_function_definitions(self):
        # Keep this scalar: a list adds another nesting level through chart-login.
        self.assertIsInstance(self.chart[".chart-registry"]["script"], str)
        helper = flatten(self.chart[".chart-registry"]["script"])[0]
        for name in ("Chart:Check Existence", "Chart:Push", "Chart:Promote"):
            with self.subTest(name=name):
                self.assertIn(helper, flatten(self.chart[name]["script"]))
        self.assertIn(helper, flatten(self.chart[".chart-login"]["script"]))

    def test_chart_scripts_have_valid_bash_syntax(self):
        bash = shutil.which("bash")
        self.assertIsNotNone(bash)
        for name, job in self.chart.items():
            if not isinstance(job, dict):
                continue
            for field in ("script", "before_script", "after_script"):
                if field not in job:
                    continue
                with self.subTest(job=name, field=field):
                    result = subprocess.run(
                        [bash, "-n"], input="\n".join(flatten(job[field])),
                        text=True, capture_output=True, check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_python_runtime_clears_entrypoint(self):
        self.assertEqual(self.python[".Python:12"]["image"]["entrypoint"], [""])

    def test_python_linters_inherit_runtime(self):
        for name, job in self.python.items():
            if name.startswith("Python:Lint:"):
                with self.subTest(job=name):
                    self.assertIn(".Python:12", job["extends"])
                    self.assertNotIn("image", job)


if __name__ == "__main__":
    unittest.main()
