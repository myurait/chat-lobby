import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { readFile } from "node:fs/promises";
import { isAbsolute, relative, resolve } from "node:path";
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

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

function sendJson(response: ServerResponse, statusCode: number, payload: unknown) {
  response.statusCode = statusCode;
  response.setHeader("Content-Type", "application/json; charset=utf-8");
  response.end(JSON.stringify(payload));
}

function notFound(response: ServerResponse) {
  sendJson(response, 404, { error: "Not found" });
}

async function readJsonBody(request: IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = [];
  for await (const chunk of request) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }

  if (chunks.length === 0) {
    return {};
  }

  return JSON.parse(Buffer.concat(chunks).toString("utf-8"));
}

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

  let stdout = "";
  try {
    const result = await execFileAsync(
      "rg",
      ["-n", "--no-heading", "--color", "never", "--max-count", String(maxResults), request.query, repoRoot],
      { maxBuffer: 1024 * 1024 },
    );
    stdout = result.stdout;
  } catch (error) {
    const candidate = error as { code?: number; stdout?: string };
    if (candidate.code !== 1) {
      throw error;
    }
    stdout = candidate.stdout ?? "";
  }

  const items = stdout
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const first = line.indexOf(":");
      const second = line.indexOf(":", first + 1);
      const filePath = line.slice(0, first);
      const lineNumber = Number(line.slice(first + 1, second));
      const content = line.slice(second + 1);
      return {
        path: filePath,
        relativePath: relative(repoRoot, filePath),
        line: lineNumber,
        content,
      };
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

  if (request.method === "POST" && url.pathname === "/search") {
    try {
      const payload = parseSearchRequest(await readJsonBody(request));
      sendJson(response, 200, await handleSearch(payload));
      return;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      sendJson(response, 400, { error: message });
      return;
    }
  }

  if (request.method === "POST" && url.pathname === "/read") {
    try {
      const payload = parseReadRequest(await readJsonBody(request));
      sendJson(response, 200, await handleRead(payload));
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
