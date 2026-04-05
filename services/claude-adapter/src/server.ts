import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { HttpError, notFound, readJsonBody, requireBearerToken, requireTokenForNonLoopbackBind, sendJson } from "../../shared/http.ts";
import { trimTasks } from "../../shared/tasks.ts";

type TaskState = "running" | "succeeded" | "failed";

type ClaudeTaskRequest = {
  prompt: string;
  workingDirectory?: string;
  permissionMode?: string;
  model?: string;
  appendSystemPrompt?: string;
  allowedTools?: string[];
};

type ClaudeTaskRecord = {
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

const PORT = Number(process.env.CLAUDE_ADAPTER_PORT ?? "8787");
const HOST = process.env.CLAUDE_ADAPTER_HOST ?? "127.0.0.1";
const CLAUDE_BIN = process.env.CLAUDE_CODE_BIN ?? "claude";
const DEFAULT_PERMISSION_MODE = process.env.CLAUDE_PERMISSION_MODE ?? "acceptEdits";
const MAX_TASKS = Number(process.env.CLAUDE_ADAPTER_MAX_TASKS ?? "50");
const API_TOKEN = process.env.CLAUDE_ADAPTER_API_TOKEN ?? process.env.CHATLOBBY_INTERNAL_API_TOKEN ?? "";

requireTokenForNonLoopbackBind("claude-adapter", HOST, API_TOKEN);

const tasks = new Map<string, ClaudeTaskRecord>();

function parseTaskRequest(input: unknown): ClaudeTaskRequest {
  if (typeof input !== "object" || input === null) {
    throw new Error("Request body must be a JSON object.");
  }

  const request = input as Record<string, unknown>;
  if (typeof request.prompt !== "string" || request.prompt.trim() === "") {
    throw new Error("`prompt` is required.");
  }

  if (request.allowedTools !== undefined && !Array.isArray(request.allowedTools)) {
    throw new Error("`allowedTools` must be an array when provided.");
  }

  return {
    prompt: request.prompt,
    workingDirectory:
      typeof request.workingDirectory === "string" && request.workingDirectory.trim() !== ""
        ? request.workingDirectory
        : process.cwd(),
    permissionMode:
      typeof request.permissionMode === "string" && request.permissionMode.trim() !== ""
        ? request.permissionMode
        : DEFAULT_PERMISSION_MODE,
    model: typeof request.model === "string" && request.model.trim() !== "" ? request.model : undefined,
    appendSystemPrompt:
      typeof request.appendSystemPrompt === "string" && request.appendSystemPrompt.trim() !== ""
        ? request.appendSystemPrompt
        : undefined,
    allowedTools: Array.isArray(request.allowedTools)
      ? request.allowedTools.filter((item): item is string => typeof item === "string" && item.trim() !== "")
      : undefined,
  };
}

function buildClaudeCommand(task: ClaudeTaskRequest): string[] {
  const command = ["-p", "--output-format", "json", "--permission-mode", task.permissionMode ?? DEFAULT_PERMISSION_MODE];

  if (task.model) {
    command.push("--model", task.model);
  }

  if (task.appendSystemPrompt) {
    command.push("--append-system-prompt", task.appendSystemPrompt);
  }

  if (task.allowedTools && task.allowedTools.length > 0) {
    command.push("--allowedTools", task.allowedTools.join(","));
  }

  command.push(task.prompt);
  return command;
}

function runTask(task: ClaudeTaskRecord, request: ClaudeTaskRequest): void {
  const child = spawn(CLAUDE_BIN, task.command, {
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
      try {
        task.result = JSON.parse(task.stdout || "{}");
      } catch {
        task.result = { raw: task.stdout };
      }
      return;
    }

    task.state = "failed";
    task.error = task.stderr || task.stdout || `Claude exited with code ${code}`;
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
      const task: ClaudeTaskRecord = {
        id,
        state: "running",
        prompt: payload.prompt,
        workingDirectory: payload.workingDirectory ?? process.cwd(),
        command: buildClaudeCommand(payload),
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
