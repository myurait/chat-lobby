import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { HttpError, notFound, readJsonBody, requireBearerToken, requireTokenForNonLoopbackBind, sendJson } from "../../shared/http.ts";

type WorkerName = "claude" | "codex" | "knowledge";

type DispatchRequest = {
  prompt?: string;
  query?: string;
  path?: string;
  repoPath?: string;
  workingDirectory?: string;
  workerHint?: WorkerName;
  maxResults?: number;
};

type WorkerRules = {
  explicitFields?: string[];
  keywords?: string[];
};

type RoutingRules = {
  workers: Record<WorkerName, WorkerRules>;
  defaultWorker: WorkerName;
};

const PORT = Number(process.env.DISPATCHER_PORT ?? "8790");
const HOST = process.env.DISPATCHER_HOST ?? "127.0.0.1";
const CLAUDE_ADAPTER_URL = process.env.CLAUDE_ADAPTER_URL ?? "http://127.0.0.1:8787";
const CODEX_ADAPTER_URL = process.env.CODEX_ADAPTER_URL ?? "http://127.0.0.1:8788";
const KNOWLEDGE_ADAPTER_URL = process.env.KNOWLEDGE_ADAPTER_URL ?? "http://127.0.0.1:8789";
const POLL_INTERVAL_MS = Number(process.env.DISPATCHER_POLL_INTERVAL_MS ?? "1000");
const POLL_TIMEOUT_MS = Number(process.env.DISPATCHER_POLL_TIMEOUT_MS ?? "180000");
const RULES_FILE = process.env.DISPATCHER_RULES_FILE ?? resolve(process.cwd(), "services/dispatcher/rules.json");
const API_TOKEN = process.env.DISPATCHER_API_TOKEN ?? process.env.CHATLOBBY_INTERNAL_API_TOKEN ?? "";
const DOWNSTREAM_API_TOKEN = process.env.DISPATCHER_DOWNSTREAM_API_TOKEN ?? process.env.CHATLOBBY_INTERNAL_API_TOKEN ?? "";

requireTokenForNonLoopbackBind("dispatcher", HOST, API_TOKEN);

function loadRoutingRules(filePath: string): RoutingRules {
  const raw = readFileSync(filePath, "utf-8");
  const parsed = JSON.parse(raw) as Partial<RoutingRules>;
  const knowledgeRules = parsed.workers?.knowledge ?? {};
  const claudeRules = parsed.workers?.claude ?? {};
  const codexRules = parsed.workers?.codex ?? {};
  const defaultWorker = parsed.defaultWorker;

  if (defaultWorker !== "claude" && defaultWorker !== "codex" && defaultWorker !== "knowledge") {
    throw new Error("Routing rules must define a valid `defaultWorker`.");
  }

  return {
    workers: {
      knowledge: {
        explicitFields: Array.isArray(knowledgeRules.explicitFields)
          ? knowledgeRules.explicitFields.filter((value): value is string => typeof value === "string" && value !== "")
          : [],
        keywords: Array.isArray(knowledgeRules.keywords)
          ? knowledgeRules.keywords.filter((value): value is string => typeof value === "string" && value !== "")
          : [],
      },
      claude: {
        explicitFields: Array.isArray(claudeRules.explicitFields)
          ? claudeRules.explicitFields.filter((value): value is string => typeof value === "string" && value !== "")
          : [],
        keywords: Array.isArray(claudeRules.keywords)
          ? claudeRules.keywords.filter((value): value is string => typeof value === "string" && value !== "")
          : [],
      },
      codex: {
        explicitFields: Array.isArray(codexRules.explicitFields)
          ? codexRules.explicitFields.filter((value): value is string => typeof value === "string" && value !== "")
          : [],
        keywords: Array.isArray(codexRules.keywords)
          ? codexRules.keywords.filter((value): value is string => typeof value === "string" && value !== "")
          : [],
      },
    },
    defaultWorker,
  };
}

const routingRules = loadRoutingRules(RULES_FILE);

function parseDispatchRequest(input: unknown): DispatchRequest {
  if (typeof input !== "object" || input === null) {
    throw new HttpError(400, "Request body must be a JSON object.");
  }

  const request = input as Record<string, unknown>;
  const prompt = typeof request.prompt === "string" ? request.prompt.trim() : "";
  const query = typeof request.query === "string" ? request.query.trim() : "";
  const path = typeof request.path === "string" ? request.path.trim() : "";

  if (!prompt && !query && !path) {
    throw new HttpError(400, "One of `prompt`, `query`, or `path` is required.");
  }

  return {
    prompt: prompt || undefined,
    query: query || undefined,
    path: path || undefined,
    repoPath: typeof request.repoPath === "string" ? request.repoPath : undefined,
    workingDirectory: typeof request.workingDirectory === "string" ? request.workingDirectory : undefined,
    workerHint:
      request.workerHint === "claude" || request.workerHint === "codex" || request.workerHint === "knowledge"
        ? request.workerHint
        : undefined,
    maxResults: typeof request.maxResults === "number" ? request.maxResults : undefined,
  };
}

function routeRequest(request: DispatchRequest): { worker: WorkerName; reason: string } {
  if (request.workerHint) {
    return { worker: request.workerHint, reason: "workerHint override" };
  }

  const explicitKnowledgeFields = new Set(routingRules.workers.knowledge.explicitFields ?? []);
  if ((request.path && explicitKnowledgeFields.has("path")) || (request.query && explicitKnowledgeFields.has("query"))) {
    return { worker: "knowledge", reason: "explicit knowledge fields" };
  }

  const prompt = (request.prompt ?? "").toLowerCase();
  const workerOrder: WorkerName[] = ["knowledge", "claude", "codex"];

  for (const worker of workerOrder) {
    const matchedKeyword = (routingRules.workers[worker].keywords ?? []).find((hint) => prompt.includes(hint.toLowerCase()));
    if (matchedKeyword) {
      return { worker, reason: `${worker} keyword match: ${matchedKeyword}` };
    }
  }

  return { worker: routingRules.defaultWorker, reason: `default fallback: ${routingRules.defaultWorker}` };
}

function normalizeKnowledgeQuery(prompt: string): string {
  return prompt
    .replace(/[。?？!！]/g, " ")
    .replace(/\b(search|find|read|show|open)\b/gi, " ")
    .replace(/\b(docs?|document|spec|adr|worklog|knowledge)\b/gi, " ")
    .replace(/(仕様|要件|文書|ドキュメント|作業ログ|ログ)/g, " ")
    .replace(/(を)?(検索して|探して|見つけて|読んで|見て|確認して|教えて)/g, " ")
    .replace(/(について|に関する|を|の)/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

async function requestJson(url: string, method: string, payload?: unknown): Promise<{ status: number; data: unknown }> {
  const body = payload === undefined ? undefined : JSON.stringify(payload);
  try {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (DOWNSTREAM_API_TOKEN) {
      headers.Authorization = `Bearer ${DOWNSTREAM_API_TOKEN}`;
    }
    const response = await fetch(url, {
      method,
      headers,
      body,
    });

    const text = await response.text();
    return {
      status: response.status,
      data: text ? JSON.parse(text) : {},
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new HttpError(502, `Downstream request failed: ${message}`);
  }
}

async function executeTaskAdapter(baseUrl: string, payload: Record<string, unknown>) {
  const created = await requestJson(`${baseUrl}/tasks`, "POST", payload);
  if (created.status !== 202) {
    throw new HttpError(502, `Task creation failed: ${JSON.stringify(created.data)}`);
  }

  const createdData = created.data as { id?: string };
  if (!createdData.id) {
    throw new HttpError(502, "Task adapter returned no task id.");
  }

  const deadline = Date.now() + POLL_TIMEOUT_MS;
  while (Date.now() < deadline) {
    const polled = await requestJson(`${baseUrl}/tasks/${createdData.id}`, "GET");
    if (polled.status !== 200) {
      throw new HttpError(502, `Task polling failed: ${JSON.stringify(polled.data)}`);
    }

    const task = polled.data as { state?: string };
    if (task.state === "succeeded" || task.state === "failed") {
      return task;
    }

    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
  }

  throw new HttpError(504, "Task timed out.");
}

async function dispatch(request: DispatchRequest) {
  const route = routeRequest(request);

  if (route.worker === "knowledge") {
    const path = request.path;
    if (path) {
      const result = await requestJson(`${KNOWLEDGE_ADAPTER_URL}/read`, "POST", {
        path,
        repoPath: request.repoPath,
      });
      if (result.status !== 200) {
        throw new HttpError(502, `Knowledge read failed: ${JSON.stringify(result.data)}`);
      }
      return { worker: route.worker, reason: route.reason, result: result.data };
    }

    const normalizedQuery = normalizeKnowledgeQuery(request.prompt ?? "");
    const resolvedQuery = (request.query ?? normalizedQuery) || request.prompt;
    const result = await requestJson(`${KNOWLEDGE_ADAPTER_URL}/search`, "POST", {
      query: resolvedQuery,
      repoPath: request.repoPath,
      maxResults: request.maxResults,
    });
    if (result.status !== 200) {
      throw new HttpError(502, `Knowledge search failed: ${JSON.stringify(result.data)}`);
    }
    return { worker: route.worker, reason: route.reason, result: result.data };
  }

  if (route.worker === "claude") {
    const result = await executeTaskAdapter(CLAUDE_ADAPTER_URL, {
      prompt: request.prompt,
      workingDirectory: request.workingDirectory,
    });
    return { worker: route.worker, reason: route.reason, result };
  }

  const result = await executeTaskAdapter(CODEX_ADAPTER_URL, {
    prompt: request.prompt,
    workingDirectory: request.workingDirectory,
  });
  return { worker: route.worker, reason: route.reason, result };
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

  if (request.method === "POST" && url.pathname === "/dispatch") {
    try {
      requireBearerToken(request, API_TOKEN);
      const payload = parseDispatchRequest(await readJsonBody(request));
      sendJson(response, 200, await dispatch(payload));
      return;
    } catch (error) {
      if (error instanceof HttpError) {
        sendJson(response, error.statusCode, { error: error.message });
        return;
      }

      const message = error instanceof Error ? error.message : String(error);
      sendJson(response, 500, { error: message });
      return;
    }
  }

  notFound(response);
});

server.listen(PORT, HOST, () => {
  console.log(JSON.stringify({ status: "listening", host: HOST, port: PORT, rulesFile: RULES_FILE }));
});
