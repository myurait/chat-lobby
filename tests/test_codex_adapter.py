import json
import os
import socket
import subprocess
import time
import unittest
import urllib.request
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT_DIR / "services" / "codex-adapter" / "src" / "server.ts"


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class CodexAdapterTests(unittest.TestCase):
    def _start_adapter(self, extra_env: dict[str, str] | None = None):
        port = find_free_port()
        env = os.environ.copy()
        env["CODEX_ADAPTER_HOST"] = "127.0.0.1"
        env["CODEX_ADAPTER_PORT"] = str(port)
        env["CODEX_CLI_BIN"] = "python3"
        if extra_env:
            env.update(extra_env)

        process = subprocess.Popen(
            ["node", str(SERVER_PATH)],
            cwd=ROOT_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        deadline = time.time() + 10
        health_url = f"http://127.0.0.1:{port}/health"
        while time.time() < deadline:
            if process.poll() is not None:
                stdout, stderr = process.communicate(timeout=1)
                self.fail(f"codex adapter exited early\nstdout:\n{stdout}\nstderr:\n{stderr}")

            try:
                with urllib.request.urlopen(health_url) as response:
                    if response.status == 200:
                        return port, process
            except Exception:  # noqa: BLE001
                time.sleep(0.1)

        self.fail("codex adapter did not become healthy in time")

    def _create_task_and_read(self, port: int, bearer_token: str | None = None):
        headers = {"Content-Type": "application/json"}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/tasks",
            data=json.dumps({"prompt": "Reply with exactly ok."}).encode("utf-8"),
            method="POST",
            headers=headers,
        )
        with urllib.request.urlopen(request) as response:
            created = json.loads(response.read().decode("utf-8"))

        deadline = time.time() + 10
        while time.time() < deadline:
            task_request = urllib.request.Request(f"http://127.0.0.1:{port}/tasks/{created['id']}")
            if bearer_token:
                task_request.add_header("Authorization", f"Bearer {bearer_token}")
            with urllib.request.urlopen(task_request) as response:
                task = json.loads(response.read().decode("utf-8"))
            if task["state"] != "running":
                return task
            time.sleep(0.1)

        self.fail("codex task did not finish in time")

    def test_default_command_uses_workspace_write_without_bypass(self):
        port, process = self._start_adapter()
        try:
            task = self._create_task_and_read(port)
            self.assertIn("--sandbox", task["command"])
            self.assertIn("workspace-write", task["command"])
            self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", task["command"])
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

    def test_explicit_opt_in_enables_bypass_flag(self):
        port, process = self._start_adapter({"CODEX_BYPASS_APPROVALS_AND_SANDBOX": "true"})
        try:
            task = self._create_task_and_read(port)
            self.assertIn("--dangerously-bypass-approvals-and-sandbox", task["command"])
            self.assertNotIn("--sandbox", task["command"])
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

    def test_bearer_token_is_required_when_configured(self):
        port, process = self._start_adapter({"CHATLOBBY_INTERNAL_API_TOKEN": "secret-token"})
        try:
            unauthorized_request = urllib.request.Request(
                f"http://127.0.0.1:{port}/tasks",
                data=json.dumps({"prompt": "Reply with exactly ok."}).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with self.assertRaises(urllib.error.HTTPError) as context:
                urllib.request.urlopen(unauthorized_request)
            self.assertEqual(context.exception.code, 401)

            task = self._create_task_and_read(port, bearer_token="secret-token")
            self.assertNotEqual(task["state"], "running")
            self.assertEqual(task["command"][0], "exec")
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
