import json
import os
import socket
import subprocess
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT_DIR / "services" / "codex-adapter" / "src" / "server.ts"


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class StatusEventServer:
    def __init__(self, token: str = "status-token"):
        self.token = token
        self.events: list[dict] = []
        self.port = find_free_port()
        self._server = ThreadingHTTPServer(("127.0.0.1", self.port), self._build_handler())
        self._server.stub = self  # type: ignore[attr-defined]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def _build_handler(self):
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                stub = self.server.stub  # type: ignore[attr-defined]
                if self.path != "/events":
                    self._send_json(404, {"error": "Not found"})
                    return

                if self.headers.get("Authorization") != f"Bearer {stub.token}":
                    self._send_json(401, {"error": "Unauthorized"})
                    return

                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
                stub.events.append(payload)
                self._send_json(202, payload)

            def log_message(self, format: str, *args) -> None:  # noqa: A003
                return

            def _send_json(self, status: int, payload: dict) -> None:
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        return Handler

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"


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

    def test_status_events_are_published_with_status_id_and_approval(self):
        status_server = StatusEventServer()
        status_server.start()
        self.addCleanup(status_server.stop)

        with tempfile.TemporaryDirectory() as temp_dir:
            fake_codex = Path(temp_dir) / "fake-codex"
            fake_codex.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env python3",
                        "import json",
                        "print(json.dumps({\"type\": \"item.completed\", \"item\": {\"type\": \"agent_message\", \"text\": \"implemented\"}}))",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)

            port, process = self._start_adapter(
                {
                    "CHATLOBBY_INTERNAL_API_TOKEN": "secret-token",
                    "STATUS_STORE_URL": status_server.base_url,
                    "STATUS_STORE_API_TOKEN": status_server.token,
                    "CODEX_CLI_BIN": str(fake_codex),
                }
            )

            try:
                task = self._create_task_and_read(port, bearer_token="secret-token")
                self.assertEqual(task["state"], "succeeded")
                self.assertTrue(task["statusId"].startswith("codex:"))

                deadline = time.time() + 5
                while time.time() < deadline:
                    if len(status_server.events) >= 2:
                        break
                    time.sleep(0.05)
                else:
                    self.fail("status events were not published in time")

                self.assertEqual(status_server.events[0]["state"], "running")
                self.assertEqual(status_server.events[0]["approvalState"], "may_require_approval")
                self.assertEqual(status_server.events[0]["statusId"], task["statusId"])
                self.assertEqual(status_server.events[-1]["state"], "succeeded")
                self.assertEqual(status_server.events[-1]["resultSummary"], "implemented")
                self.assertEqual(status_server.events[-1]["statusId"], task["statusId"])
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
