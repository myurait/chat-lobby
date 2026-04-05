import json
import os
import socket
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT_DIR / "services" / "knowledge-adapter" / "src" / "server.ts"


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class KnowledgeAdapterTests(unittest.TestCase):
    def test_read_accepts_repo_relative_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            target = repo_root / "README.ja.md"
            target.write_text("relative path content", encoding="utf-8")

            port = find_free_port()
            env = os.environ.copy()
            env["KNOWLEDGE_ADAPTER_HOST"] = "127.0.0.1"
            env["KNOWLEDGE_ADAPTER_PORT"] = str(port)
            env["KNOWLEDGE_REPO_PATH"] = str(repo_root)

            process = subprocess.Popen(
                ["node", str(SERVER_PATH)],
                cwd=ROOT_DIR,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            try:
                deadline = time.time() + 10
                health_url = f"http://127.0.0.1:{port}/health"
                while time.time() < deadline:
                    if process.poll() is not None:
                        stdout, stderr = process.communicate(timeout=1)
                        self.fail(f"knowledge adapter exited early\nstdout:\n{stdout}\nstderr:\n{stderr}")

                    try:
                        with urllib.request.urlopen(health_url) as response:
                            if response.status == 200:
                                break
                    except urllib.error.URLError:
                        time.sleep(0.1)
                else:
                    self.fail("knowledge adapter did not become healthy in time")

                request = urllib.request.Request(
                    f"http://127.0.0.1:{port}/read",
                    data=json.dumps({"path": "README.ja.md"}).encode("utf-8"),
                    method="POST",
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(request) as response:
                    payload = json.loads(response.read().decode("utf-8"))

                self.assertEqual(response.status, 200)
                self.assertEqual(payload["relativePath"], "README.ja.md")
                self.assertIn("relative path content", payload["content"])
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                if process.stdout is not None:
                    process.stdout.close()
                if process.stderr is not None:
                    process.stderr.close()

    def test_search_supports_path_match_fallback(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "README.ja.md").write_text("plain text", encoding="utf-8")

            port = find_free_port()
            env = os.environ.copy()
            env["KNOWLEDGE_ADAPTER_HOST"] = "127.0.0.1"
            env["KNOWLEDGE_ADAPTER_PORT"] = str(port)
            env["KNOWLEDGE_REPO_PATH"] = str(repo_root)

            process = subprocess.Popen(
                ["node", str(SERVER_PATH)],
                cwd=ROOT_DIR,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            try:
                deadline = time.time() + 10
                health_url = f"http://127.0.0.1:{port}/health"
                while time.time() < deadline:
                    if process.poll() is not None:
                        stdout, stderr = process.communicate(timeout=1)
                        self.fail(f"knowledge adapter exited early\nstdout:\n{stdout}\nstderr:\n{stderr}")

                    try:
                        with urllib.request.urlopen(health_url) as response:
                            if response.status == 200:
                                break
                    except urllib.error.URLError:
                        time.sleep(0.1)
                else:
                    self.fail("knowledge adapter did not become healthy in time")

                request = urllib.request.Request(
                    f"http://127.0.0.1:{port}/search",
                    data=json.dumps({"query": "README.ja.md"}).encode("utf-8"),
                    method="POST",
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(request) as response:
                    payload = json.loads(response.read().decode("utf-8"))

                self.assertEqual(response.status, 200)
                self.assertEqual(payload["items"][0]["relativePath"], "README.ja.md")
                self.assertEqual(payload["items"][0]["content"], "[path match]")
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                if process.stdout is not None:
                    process.stdout.close()
                if process.stderr is not None:
                    process.stderr.close()

    def test_search_treats_option_like_query_as_pattern(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "README.md").write_text("plain text", encoding="utf-8")

            port = find_free_port()
            env = os.environ.copy()
            env["KNOWLEDGE_ADAPTER_HOST"] = "127.0.0.1"
            env["KNOWLEDGE_ADAPTER_PORT"] = str(port)
            env["KNOWLEDGE_REPO_PATH"] = str(repo_root)

            process = subprocess.Popen(
                ["node", str(SERVER_PATH)],
                cwd=ROOT_DIR,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            try:
                deadline = time.time() + 10
                health_url = f"http://127.0.0.1:{port}/health"
                while time.time() < deadline:
                    if process.poll() is not None:
                        stdout, stderr = process.communicate(timeout=1)
                        self.fail(f"knowledge adapter exited early\nstdout:\n{stdout}\nstderr:\n{stderr}")

                    try:
                        with urllib.request.urlopen(health_url) as response:
                            if response.status == 200:
                                break
                    except urllib.error.URLError:
                        time.sleep(0.1)
                else:
                    self.fail("knowledge adapter did not become healthy in time")

                request = urllib.request.Request(
                    f"http://127.0.0.1:{port}/search",
                    data=json.dumps({"query": "--files"}).encode("utf-8"),
                    method="POST",
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(request) as response:
                    payload = json.loads(response.read().decode("utf-8"))

                self.assertEqual(response.status, 200)
                self.assertEqual(payload["items"], [])
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                if process.stdout is not None:
                    process.stdout.close()
                if process.stderr is not None:
                    process.stderr.close()


if __name__ == "__main__":
    unittest.main()
