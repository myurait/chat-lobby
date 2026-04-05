import { HttpError } from "../../shared/http.ts";

export type WorkerName = "claude" | "codex" | "knowledge";

export type DispatchRequest = {
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

export type RoutingRules = {
  workers: Record<WorkerName, WorkerRules>;
  defaultWorker: WorkerName;
};

export function parseDispatchRequest(input: unknown): DispatchRequest {
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

export function routeRequest(
  request: DispatchRequest,
  routingRules: RoutingRules,
): { worker: WorkerName; reason: string } {
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

export function normalizeKnowledgeQuery(prompt: string): string {
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
