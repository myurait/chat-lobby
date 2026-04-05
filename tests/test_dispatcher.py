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
SERVER_PATH = ROOT_DIR / "services" / "dispatcher" / "src" / "server.ts"


def find_free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class StubServer:
    def __init__(self, kind: str, task_result: dict | None = None, search_result: dict | None = None, read_result: dict | None = None):
        self.kind = kind
        self.task_result = task_result or {}
        self.search_result = search_result or {}
        self.read_result = read_result or {}
        self.requests: list[tuple[str, dict | None]] = []
        self.port = find_free_port()
        self._server = ThreadingHTTPServer(("127.0.0.1", self.port), self._build_handler())
        self._server.stub = self  # type: ignore[attr-defined]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def _build_handler(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                stub = self.server.stub  # type: ignore[attr-defined]
                if self.path == "/health":
                    self._send_json(200, {"status": True})
                    return

                if self.path.startswith("/tasks/") and stub.kind in {"codex", "claude"}:
                    self._send_json(200, stub.task_result)
                    return

                self._send_json(404, {"error": "Not found"})

            def do_POST(self) -> None:  # noqa: N802
                stub = self.server.stub  # type: ignore[attr-defined]
                payload = self._read_json()
                stub.requests.append((self.path, payload))

                if self.path == "/tasks" and stub.kind in {"codex", "claude"}:
                    self._send_json(202, {"id": f"{stub.kind}-task", "state": "running"})
                    return

                if self.path == "/search" and stub.kind == "knowledge":
                    self._send_json(200, stub.search_result)
                    return

                if self.path == "/read" and stub.kind == "knowledge":
                    self._send_json(200, stub.read_result)
                    return

                self._send_json(404, {"error": "Not found"})

            def log_message(self, format: str, *args) -> None:  # noqa: A003
                return

            def _read_json(self) -> dict:
                length = int(self.headers.get("Content-Length", "0"))
                if length == 0:
                    return {}
                return json.loads(self.rfile.read(length).decode("utf-8"))

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


class DispatcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.codex_stub = StubServer(
            "codex",
            task_result={
                "id": "codex-task",
                "state": "succeeded",
                "result": {"message": "implemented"},
            },
        )
        self.claude_stub = StubServer(
            "claude",
            task_result={
                "id": "claude-task",
                "state": "succeeded",
                "result": {"result": "investigated"},
            },
        )
        self.knowledge_stub = StubServer(
            "knowledge",
            search_result={
                "repoRoot": "/tmp/repo",
                "items": [{"relativePath": "specs/example.md", "line": 3, "content": "match"}],
            },
            read_result={
                "repoRoot": "/tmp/repo",
                "path": "/tmp/repo/specs/example.md",
                "relativePath": "specs/example.md",
                "content": "document body",
            },
        )

        for stub in (self.codex_stub, self.claude_stub, self.knowledge_stub):
            stub.start()
            self.addCleanup(stub.stop)

        self.port = find_free_port()
        env = os.environ.copy()
        env["DISPATCHER_HOST"] = "127.0.0.1"
        env["DISPATCHER_PORT"] = str(self.port)
        env["CLAUDE_ADAPTER_URL"] = self.claude_stub.base_url
        env["CODEX_ADAPTER_URL"] = self.codex_stub.base_url
        env["KNOWLEDGE_ADAPTER_URL"] = self.knowledge_stub.base_url

        self.process = subprocess.Popen(
            ["node", str(SERVER_PATH)],
            cwd=ROOT_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(self._cleanup_process)
        self._wait_for_server()

    def _cleanup_process(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        if self.process.stdout is not None:
            self.process.stdout.close()
        if self.process.stderr is not None:
            self.process.stderr.close()

    def _wait_for_server(self) -> None:
        deadline = time.time() + 10
        last_error = None
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/health", timeout=1) as response:
                    if response.status == 200:
                        return
            except Exception as error:  # noqa: BLE001
                last_error = error
                time.sleep(0.1)

        self.fail(f"dispatcher did not start: {last_error}")

    def _post_json(self, payload: dict, bearer_token: str | None = None) -> tuple[int, dict]:
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/dispatch",
            data=body,
            method="POST",
            headers=headers,
        )

        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read().decode("utf-8"))

    def test_query_field_routes_to_knowledge(self) -> None:
        status, data = self._post_json({"query": "ChatLobby"})

        self.assertEqual(status, 200)
        self.assertEqual(data["worker"], "knowledge")
        self.assertEqual(data["result"]["items"][0]["relativePath"], "specs/example.md")
        self.assertEqual(self.knowledge_stub.requests[0][0], "/search")
        self.assertEqual(self.knowledge_stub.requests[0][1]["query"], "ChatLobby")

    def test_path_field_routes_to_knowledge_read(self) -> None:
        status, data = self._post_json({"path": "specs/example.md"})

        self.assertEqual(status, 200)
        self.assertEqual(data["worker"], "knowledge")
        self.assertEqual(data["result"]["content"], "document body")
        self.assertEqual(self.knowledge_stub.requests[0][0], "/read")
        self.assertEqual(self.knowledge_stub.requests[0][1]["path"], "specs/example.md")

    def test_implementation_prompt_routes_to_codex(self) -> None:
        status, data = self._post_json({"prompt": "実装して", "workingDirectory": "/tmp/worktree"})

        self.assertEqual(status, 200)
        self.assertEqual(data["worker"], "codex")
        self.assertIn("keyword match", data["reason"])
        self.assertEqual(self.codex_stub.requests[0][0], "/tasks")
        self.assertEqual(self.codex_stub.requests[0][1]["prompt"], "実装して")
        self.assertEqual(self.codex_stub.requests[0][1]["workingDirectory"], "/tmp/worktree")

    def test_worker_hint_overrides_keyword_routing(self) -> None:
        status, data = self._post_json({"prompt": "実装して", "workerHint": "claude"})

        self.assertEqual(status, 200)
        self.assertEqual(data["worker"], "claude")
        self.assertEqual(data["reason"], "workerHint override")
        self.assertEqual(self.claude_stub.requests[0][0], "/tasks")
        self.assertEqual(self.claude_stub.requests[0][1]["prompt"], "実装して")

    def test_knowledge_prompt_is_normalized_before_search(self) -> None:
        status, data = self._post_json({"prompt": "ChatLobby の仕様を検索して"})

        self.assertEqual(status, 200)
        self.assertEqual(data["worker"], "knowledge")
        self.assertEqual(self.knowledge_stub.requests[0][1]["query"], "ChatLobby")

    def test_dispatch_requires_bearer_token_when_configured(self) -> None:
        self._cleanup_process()
        env = os.environ.copy()
        env["DISPATCHER_HOST"] = "127.0.0.1"
        env["DISPATCHER_PORT"] = str(self.port)
        env["CLAUDE_ADAPTER_URL"] = self.claude_stub.base_url
        env["CODEX_ADAPTER_URL"] = self.codex_stub.base_url
        env["KNOWLEDGE_ADAPTER_URL"] = self.knowledge_stub.base_url
        env["CHATLOBBY_INTERNAL_API_TOKEN"] = "secret-token"
        self.process = subprocess.Popen(
            ["node", str(SERVER_PATH)],
            cwd=ROOT_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self._wait_for_server()

        status, data = self._post_json({"prompt": "実装して"})
        self.assertEqual(status, 401)
        self.assertIn("token", data["error"])

        status, data = self._post_json({"prompt": "実装して"}, bearer_token="secret-token")
        self.assertEqual(status, 200)
        self.assertEqual(data["worker"], "codex")


if __name__ == "__main__":
    unittest.main()
