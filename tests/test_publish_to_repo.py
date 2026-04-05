import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT_DIR / "tools" / "publish_to_repo.py"

spec = importlib.util.spec_from_file_location("publish_to_repo", MODULE_PATH)
publish_to_repo = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = publish_to_repo
spec.loader.exec_module(publish_to_repo)


class PublishToolTests(unittest.TestCase):
    def test_slugify_normalizes_title(self):
        self.assertEqual(publish_to_repo.slugify("My Great Spec"), "my-great-spec")

    def test_publish_document_writes_into_expected_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            for name in ("docs", "specs", "decisions", "worklog"):
                (repo_path / name).mkdir()

            request = publish_to_repo.PublishRequest(
                repo_path=repo_path,
                kind="spec",
                title="Routing Policy",
                slug="routing-policy",
                body="A short summary.",
                date="2026-04-05",
                author="ChatLobby",
            )

            target_path = publish_to_repo.publish_document(request)

            self.assertEqual(target_path, repo_path / "specs" / "2026-04-05-routing-policy.md")
            self.assertIn("Routing Policy", target_path.read_text(encoding="utf-8"))
            self.assertIn("A short summary.", target_path.read_text(encoding="utf-8"))

    def test_publish_document_requires_canonical_layout(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "specs").mkdir()

            request = publish_to_repo.PublishRequest(
                repo_path=repo_path,
                kind="adr",
                title="Use Open WebUI",
                slug="use-open-webui",
                body="Context",
                date="2026-04-05",
                author="ChatLobby",
            )

            with self.assertRaises(FileNotFoundError):
                publish_to_repo.publish_document(request)

    def test_cli_rejects_duplicate_target_without_overwrite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            for name in ("docs", "specs", "decisions", "worklog"):
                (repo_path / name).mkdir()

            target = repo_path / "worklog" / "2026-04-05-phase-b.md"
            target.write_text("existing", encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    str(MODULE_PATH),
                    "--repo",
                    str(repo_path),
                    "--kind",
                    "worklog",
                    "--title",
                    "Phase B",
                    "--slug",
                    "phase-b",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Target file already exists", result.stderr)


if __name__ == "__main__":
    unittest.main()
