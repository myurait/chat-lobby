import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { HttpError, notFound, readJsonBody, requireBearerToken, requireTokenForNonLoopbackBind, sendJson } from "../../shared/http.ts";
import { trimTasks } from "../../shared/tasks.ts";

type TaskState = "running" | "succeeded" | "failed";

type CodexTaskRequest = {
  prompt: string;
  workingDirectory?: string;
  model?: string;
  sandboxMode?: "read-only" | "workspace-write" | "danger-full-access";
  skipGitRepoCheck?: boolean;
  bypassApprovalsAndSandbox?: boolean;
};

type CodexTaskRecord = {
  id: string;
  state: TaskState;
  prompt: string;
  workingDirectory: string;
  command: string[];
  createdAt: string;
  completedAt?: string;
  exitCode?: number | null;
  stdout?: string;
  stderr?: string;
  result?: unknown;
  error?: string;
};

const PORT = Number(process.env.CODEX_ADAPTER_PORT ?? "8788");
const HOST = process.env.CODEX_ADAPTER_HOST ?? "127.0.0.1";
const CODEX_BIN = process.env.CODEX_CLI_BIN ?? "codex";
const DEFAULT_SANDBOX_MODE =
  (process.env.CODEX_SANDBOX_MODE as CodexTaskRequest["sandboxMode"] | undefined) ?? "workspace-write";
const DEFAULT_SKIP_GIT_REPO_CHECK = process.env.CODEX_SKIP_GIT_REPO_CHECK !== "false";
const DEFAULT_BYPASS_APPROVALS = process.env.CODEX_BYPASS_APPROVALS_AND_SANDBOX === "true";
const MAX_TASKS = Number(process.env.CODEX_ADAPTER_MAX_TASKS ?? "50");
const API_TOKEN = process.env.CODEX_ADAPTER_API_TOKEN ?? process.env.CHATLOBBY_INTERNAL_API_TOKEN ?? "";

requireTokenForNonLoopbackBind("codex-adapter", HOST, API_TOKEN);

const tasks = new Map<string, CodexTaskRecord>();

function parseTaskRequest(input: unknown): CodexTaskRequest {
  if (typeof input !== "object" || input === null) {
    throw new Error("Request body must be a JSON object.");
  }

  const request = input as Record<string, unknown>;
  if (typeof request.prompt !== "string" || request.prompt.trim() === "") {
    throw new Error("`prompt` is required.");
  }

  const sandboxMode =
    typeof request.sandboxMode === "string" &&
    ["read-only", "workspace-write", "danger-full-access"].includes(request.sandboxMode)
      ? (request.sandboxMode as CodexTaskRequest["sandboxMode"])
      : DEFAULT_SANDBOX_MODE;

  return {
    prompt: request.prompt,
    workingDirectory:
      typeof request.workingDirectory === "string" && request.workingDirectory.trim() !== ""
        ? request.workingDirectory
        : process.cwd(),
    model: typeof request.model === "string" && request.model.trim() !== "" ? request.model : undefined,
    sandboxMode,
    skipGitRepoCheck:
      typeof request.skipGitRepoCheck === "boolean" ? request.skipGitRepoCheck : DEFAULT_SKIP_GIT_REPO_CHECK,
    bypassApprovalsAndSandbox:
      typeof request.bypassApprovalsAndSandbox === "boolean"
        ? request.bypassApprovalsAndSandbox
        : DEFAULT_BYPASS_APPROVALS,
  };
}

function buildCodexCommand(task: CodexTaskRequest): string[] {
  const command = ["exec", "--json"];

  if (task.skipGitRepoCheck) {
    command.push("--skip-git-repo-check");
  }

  if (task.bypassApprovalsAndSandbox) {
    command.push("--dangerously-bypass-approvals-and-sandbox");
  } else if (task.sandboxMode) {
    command.push("--sandbox", task.sandboxMode);
  }

  if (task.model) {
    command.push("--model", task.model);
  }

  command.push(task.prompt);
  return command;
}

function parseCodexJsonl(stdout: string): unknown {
  const events = stdout
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.startsWith("{"))
    .map((line) => JSON.parse(line));

  const completedAgentMessage = events.findLast(
    (event) => event.type === "item.completed" && event.item?.type === "agent_message",
  );
  if (completedAgentMessage?.item?.text) {
    return {
      message: completedAgentMessage.item.text,
      events,
    };
  }

  return { events };
}

function runTask(task: CodexTaskRecord, request: CodexTaskRequest): void {
  const child = spawn(CODEX_BIN, task.command, {
    cwd: request.workingDirectory,
    env: process.env,
    stdio: ["ignore", "pipe", "pipe"],
  });

  let stdout = "";
  let stderr = "";

  child.stdout.on("data", (chunk) => {
    stdout += chunk.toString();
  });

  child.stderr.on("data", (chunk) => {
    stderr += chunk.toString();
  });

  child.on("close", (code) => {
    task.completedAt = new Date().toISOString();
    task.exitCode = code;
    task.stdout = stdout.trim();
    task.stderr = stderr.trim();

    if (code === 0) {
      task.state = "succeeded";
      task.result = parseCodexJsonl(task.stdout ?? "");
      return;
    }

    task.state = "failed";
    task.error = task.stderr || task.stdout || `Codex exited with code ${code}`;
  });

  child.on("error", (error) => {
    task.completedAt = new Date().toISOString();
    task.exitCode = null;
    task.state = "failed";
    task.error = error.message;
  });
}

const server = createServer(async (request, response) => {
  if (!request.url) {
    notFound(response);
    return;
  }

  const url = new URL(request.url, `http://${request.headers.host ?? `${HOST}:${PORT}`}`);

  if (request.method === "GET" && url.pathname === "/health") {
    sendJson(response, 200, { status: true });
    return;
  }

  try {
    requireBearerToken(request, API_TOKEN);
  } catch (error) {
    if (error instanceof HttpError) {
      sendJson(response, error.statusCode, { error: error.message });
      return;
    }
    throw error;
  }

  if (request.method === "GET" && url.pathname === "/tasks") {
    sendJson(response, 200, {
      items: Array.from(tasks.values()).map((task) => ({
        id: task.id,
        state: task.state,
        createdAt: task.createdAt,
        completedAt: task.completedAt,
        workingDirectory: task.workingDirectory,
      })),
    });
    return;
  }

  if (request.method === "GET" && url.pathname.startsWith("/tasks/")) {
    const taskId = url.pathname.slice("/tasks/".length);
    const task = tasks.get(taskId);
    if (!task) {
      notFound(response);
      return;
    }

    sendJson(response, 200, task);
    return;
  }

  if (request.method === "POST" && url.pathname === "/tasks") {
    try {
      const payload = parseTaskRequest(await readJsonBody(request));
      const id = randomUUID();
      const task: CodexTaskRecord = {
        id,
        state: "running",
        prompt: payload.prompt,
        workingDirectory: payload.workingDirectory ?? process.cwd(),
        command: buildCodexCommand(payload),
        createdAt: new Date().toISOString(),
      };

      trimTasks(tasks, MAX_TASKS);
      tasks.set(id, task);
      runTask(task, payload);

      sendJson(response, 202, {
        id: task.id,
        state: task.state,
        createdAt: task.createdAt,
      });
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      sendJson(response, 400, { error: message });
      return;
    }
  }

  notFound(response);
});

server.listen(PORT, HOST, () => {
  console.log(JSON.stringify({ status: "listening", host: HOST, port: PORT }));
});
