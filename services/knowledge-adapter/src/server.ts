import { execFile, spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { promisify } from "node:util";
import { readFile } from "node:fs/promises";
import { isAbsolute, relative, resolve } from "node:path";
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { HttpError, notFound, readJsonBody, requireBearerToken, requireTokenForNonLoopbackBind, sendJson } from "../../shared/http.ts";
import { buildStatusId, publishStatusEvent } from "../../shared/status.ts";

const execFileAsync = promisify(execFile);

type SearchRequest = {
  query: string;
  repoPath?: string;
  maxResults?: number;
};

type ReadRequest = {
  path: string;
  repoPath?: string;
  maxBytes?: number;
};

const PORT = Number(process.env.KNOWLEDGE_ADAPTER_PORT ?? "8789");
const HOST = process.env.KNOWLEDGE_ADAPTER_HOST ?? "127.0.0.1";
const DEFAULT_REPO_PATH = process.env.KNOWLEDGE_REPO_PATH ?? resolve(process.cwd(), "workspace/templates/chatlobby-canonical");
const MAX_RESULTS = Number(process.env.KNOWLEDGE_MAX_RESULTS ?? "10");
const MAX_BYTES = Number(process.env.KNOWLEDGE_MAX_BYTES ?? "12000");
const API_TOKEN = process.env.KNOWLEDGE_ADAPTER_API_TOKEN ?? process.env.CHATLOBBY_INTERNAL_API_TOKEN ?? "";
const STATUS_STORE_URL = process.env.STATUS_STORE_URL ?? process.env.CHATLOBBY_STATUS_STORE_URL ?? "";
const STATUS_STORE_TOKEN = process.env.STATUS_STORE_API_TOKEN ?? process.env.CHATLOBBY_INTERNAL_API_TOKEN ?? "";

requireTokenForNonLoopbackBind("knowledge-adapter", HOST, API_TOKEN);

function ensureRepoRoot(candidate?: string): string {
  return resolve(candidate && candidate.trim() !== "" ? candidate : DEFAULT_REPO_PATH);
}

function ensurePathInsideRepo(repoRoot: string, pathValue: string): string {
  const resolved = isAbsolute(pathValue) ? resolve(pathValue) : resolve(repoRoot, pathValue);
  const rel = relative(repoRoot, resolved);
  if (rel !== "" && (rel.startsWith("..") || isAbsolute(rel))) {
    throw new Error("Path must stay inside the configured repository root.");
  }
  return resolved;
}

function parseSearchRequest(input: unknown): SearchRequest {
  if (typeof input !== "object" || input === null) {
    throw new Error("Request body must be a JSON object.");
  }

  const request = input as Record<string, unknown>;
  if (typeof request.query !== "string" || request.query.trim() === "") {
    throw new Error("`query` is required.");
  }

  return {
    query: request.query.trim(),
    repoPath: typeof request.repoPath === "string" ? request.repoPath : undefined,
    maxResults: typeof request.maxResults === "number" ? request.maxResults : undefined,
  };
}

function parseReadRequest(input: unknown): ReadRequest {
  if (typeof input !== "object" || input === null) {
    throw new Error("Request body must be a JSON object.");
  }

  const request = input as Record<string, unknown>;
  if (typeof request.path !== "string" || request.path.trim() === "") {
    throw new Error("`path` is required.");
  }

  return {
    path: request.path.trim(),
    repoPath: typeof request.repoPath === "string" ? request.repoPath : undefined,
    maxBytes: typeof request.maxBytes === "number" ? request.maxBytes : undefined,
  };
}

async function handleSearch(request: SearchRequest) {
  const repoRoot = ensureRepoRoot(request.repoPath);
  const maxResults = Math.max(1, Math.min(request.maxResults ?? MAX_RESULTS, MAX_RESULTS));

  const items = await new Promise<
    Array<{ path: string; relativePath: string; line: number; content: string }>
  >((resolvePromise, rejectPromise) => {
    const child = spawn(
      "rg",
      ["-n", "--no-heading", "--color", "never", "--max-count", "1", "--", request.query, repoRoot],
      { stdio: ["ignore", "pipe", "pipe"] },
    );

    let stdoutBuffer = "";
    let stderr = "";
    const matches: Array<{ path: string; relativePath: string; line: number; content: string }> = [];
    let settled = false;

    const processBuffer = (flush: boolean) => {
      const lines = stdoutBuffer.split("\n");
      stdoutBuffer = flush ? "" : (lines.pop() ?? "");

      for (const rawLine of lines) {
        const line = rawLine.trim();
        if (!line) {
          continue;
        }

        const first = line.indexOf(":");
        const second = line.indexOf(":", first + 1);
        if (first === -1 || second === -1) {
          continue;
        }

        const filePath = line.slice(0, first);
        const lineNumber = Number(line.slice(first + 1, second));
        const content = line.slice(second + 1);
        matches.push({
          path: filePath,
          relativePath: relative(repoRoot, filePath),
          line: lineNumber,
          content,
        });

        if (matches.length >= maxResults && child.exitCode === null) {
          child.kill();
          break;
        }
      }
    };

    child.stdout.on("data", (chunk) => {
      stdoutBuffer += chunk.toString();
      processBuffer(false);
    });

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    child.on("error", (error) => {
      if (!settled) {
        settled = true;
        rejectPromise(error);
      }
    });

    child.on("close", (code, signal) => {
      if (settled) {
        return;
      }

      processBuffer(true);

      if (signal === "SIGTERM" && matches.length >= maxResults) {
        settled = true;
        resolvePromise(matches.slice(0, maxResults));
        return;
      }

      if (code !== 0 && code !== 1) {
        settled = true;
        rejectPromise(new Error(stderr.trim() || `rg exited with code ${code}`));
        return;
      }

      settled = true;
      resolvePromise(matches.slice(0, maxResults));
    });
  });

  if (items.length > 0) {
    return { repoRoot, items };
  }

  const fileList = await execFileAsync("rg", ["--files", repoRoot], { maxBuffer: 1024 * 1024 });
  const normalizedQuery = request.query.toLowerCase();
  const fileMatches = fileList.stdout
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line !== "" && line.toLowerCase().includes(normalizedQuery))
    .slice(0, maxResults)
    .map((filePath) => ({
      path: filePath,
      relativePath: relative(repoRoot, filePath),
      line: 1,
      content: "[path match]",
    }));

  return { repoRoot, items: fileMatches };
}

async function handleRead(request: ReadRequest) {
  const repoRoot = ensureRepoRoot(request.repoPath);
  const maxBytes = Math.max(1, Math.min(request.maxBytes ?? MAX_BYTES, MAX_BYTES));
  const absolutePath = ensurePathInsideRepo(repoRoot, request.path);
  const content = await readFile(absolutePath, "utf-8");
  const sliced = content.length > maxBytes ? `${content.slice(0, maxBytes)}\n\n[truncated]` : content;
  return {
    repoRoot,
    path: absolutePath,
    relativePath: relative(repoRoot, absolutePath),
    content: sliced,
  };
}

const server = createServer(async (request, response) => {
  if (!request.url) {
    notFound(response);
    return;
  }

  const url = new URL(request.url, `http://${request.headers.host ?? `${HOST}:${PORT}`}`);

  if (request.method === "GET" && url.pathname === "/health") {
    sendJson(response, 200, { status: true, repoRoot: DEFAULT_REPO_PATH });
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

  if (request.method === "POST" && url.pathname === "/search") {
    try {
      const taskId = randomUUID();
      const statusId = buildStatusId("knowledge", taskId);
      const payload = parseSearchRequest(await readJsonBody(request));
      void publishStatusEvent(STATUS_STORE_URL, STATUS_STORE_TOKEN, {
        statusId,
        taskId,
        worker: "knowledge",
        state: "running",
        title: "Knowledge search",
        prompt: payload.query,
        workingDirectory: ensureRepoRoot(payload.repoPath),
        currentStep: "search started",
        lastAction: "rg search",
        approvalState: "not_required",
      }).catch(() => {});
      const result = await handleSearch(payload);
      void publishStatusEvent(STATUS_STORE_URL, STATUS_STORE_TOKEN, {
        statusId,
        taskId,
        worker: "knowledge",
        state: "succeeded",
        title: "Knowledge search",
        prompt: payload.query,
        workingDirectory: result.repoRoot,
        currentStep: "completed",
        lastAction: "search result returned",
        approvalState: "not_required",
        resultSummary: `${result.items.length} match(es)`,
      }).catch(() => {});
      sendJson(response, 200, { statusId, ...result });
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      sendJson(response, 400, { error: message });
      return;
    }
  }

  if (request.method === "POST" && url.pathname === "/read") {
    try {
      const taskId = randomUUID();
      const statusId = buildStatusId("knowledge", taskId);
      const payload = parseReadRequest(await readJsonBody(request));
      void publishStatusEvent(STATUS_STORE_URL, STATUS_STORE_TOKEN, {
        statusId,
        taskId,
        worker: "knowledge",
        state: "running",
        title: "Knowledge read",
        prompt: payload.path,
        workingDirectory: ensureRepoRoot(payload.repoPath),
        currentStep: "read started",
        lastAction: "file read",
        approvalState: "not_required",
      }).catch(() => {});
      const result = await handleRead(payload);
      void publishStatusEvent(STATUS_STORE_URL, STATUS_STORE_TOKEN, {
        statusId,
        taskId,
        worker: "knowledge",
        state: "succeeded",
        title: "Knowledge read",
        prompt: payload.path,
        workingDirectory: result.repoRoot,
        currentStep: "completed",
        lastAction: "file read returned",
        approvalState: "not_required",
        resultSummary: result.relativePath,
      }).catch(() => {});
      sendJson(response, 200, { statusId, ...result });
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
  console.log(JSON.stringify({ status: "listening", host: HOST, port: PORT, repoRoot: DEFAULT_REPO_PATH }));
});
