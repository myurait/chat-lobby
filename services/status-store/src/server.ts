import { createServer } from "node:http";
import { HttpError, notFound, readJsonBody, requireBearerToken, requireTokenForNonLoopbackBind, sendJson } from "../../shared/http.ts";
import { buildStatusId, type StatusEvent, type StatusRecord, type WorkerName } from "../../shared/status.ts";

const PORT = Number(process.env.STATUS_STORE_PORT ?? "8791");
const HOST = process.env.STATUS_STORE_HOST ?? "127.0.0.1";
const API_TOKEN = process.env.STATUS_STORE_API_TOKEN ?? process.env.CHATLOBBY_INTERNAL_API_TOKEN ?? "";
const MAX_TASKS = Number(process.env.STATUS_STORE_MAX_TASKS ?? "200");

requireTokenForNonLoopbackBind("status-store", HOST, API_TOKEN);

const tasks = new Map<string, StatusRecord>();

function ensureString(value: unknown): string | undefined {
  return typeof value === "string" && value.trim() !== "" ? value : undefined;
}

function ensureApprovalState(value: unknown): StatusRecord["approvalState"] {
  return value === "not_required" || value === "may_require_approval" || value === "bypassed" || value === "unknown"
    ? value
    : undefined;
}

function parseStatusEvent(input: unknown): StatusEvent {
  if (typeof input !== "object" || input === null) {
    throw new HttpError(400, "Request body must be a JSON object.");
  }

  const request = input as Record<string, unknown>;
  const taskId = ensureString(request.taskId);
  if (!taskId) {
    throw new HttpError(400, "`taskId` is required.");
  }

  const worker = request.worker;
  if (worker !== "claude" && worker !== "codex" && worker !== "knowledge") {
    throw new HttpError(400, "`worker` must be one of claude, codex, knowledge.");
  }

  const state = request.state;
  if (state !== "running" && state !== "succeeded" && state !== "failed") {
    throw new HttpError(400, "`state` must be one of running, succeeded, failed.");
  }

  const metadata =
    typeof request.metadata === "object" && request.metadata !== null && !Array.isArray(request.metadata)
      ? (request.metadata as Record<string, unknown>)
      : undefined;

  return {
    statusId: ensureString(request.statusId),
    taskId,
    worker,
    state,
    title: ensureString(request.title),
    prompt: ensureString(request.prompt),
    workingDirectory: ensureString(request.workingDirectory),
    currentStep: ensureString(request.currentStep),
    lastAction: ensureString(request.lastAction),
    approvalState: ensureApprovalState(request.approvalState),
    resultSummary: ensureString(request.resultSummary),
    error: ensureString(request.error),
    createdAt: ensureString(request.createdAt),
    completedAt: ensureString(request.completedAt),
    metadata,
  };
}

function trimStatusRecords() {
  if (tasks.size <= MAX_TASKS) {
    return;
  }

  const oldest = Array.from(tasks.values())
    .sort((left, right) => left.updatedAt.localeCompare(right.updatedAt))
    .slice(0, tasks.size - MAX_TASKS);

  for (const item of oldest) {
    tasks.delete(item.statusId);
  }
}

function mergeStatusEvent(event: StatusEvent): StatusRecord {
  const statusId = event.statusId ?? buildStatusId(event.worker, event.taskId);
  const now = new Date().toISOString();
  const current = tasks.get(statusId);
  const next: StatusRecord = {
    statusId,
    taskId: event.taskId,
    worker: event.worker,
    state: event.state,
    title: event.title ?? current?.title,
    prompt: event.prompt ?? current?.prompt,
    workingDirectory: event.workingDirectory ?? current?.workingDirectory,
    currentStep: event.currentStep ?? current?.currentStep,
    lastAction: event.lastAction ?? current?.lastAction,
    approvalState: event.approvalState ?? current?.approvalState ?? "unknown",
    resultSummary: event.resultSummary ?? current?.resultSummary,
    error: event.error ?? current?.error,
    createdAt: current?.createdAt ?? event.createdAt ?? now,
    completedAt:
      event.completedAt ??
      (event.state === "succeeded" || event.state === "failed" ? now : current?.completedAt),
    metadata: event.metadata ?? current?.metadata,
    updatedAt: now,
  };

  tasks.set(statusId, next);
  trimStatusRecords();
  return next;
}

function listTasks(url: URL): StatusRecord[] {
  const state = url.searchParams.get("state");
  const worker = url.searchParams.get("worker");
  const limit = Math.max(1, Math.min(Number(url.searchParams.get("limit") ?? "20"), 100));

  return Array.from(tasks.values())
    .filter((item) => (state ? item.state === state : true))
    .filter((item) => (worker ? item.worker === (worker as WorkerName) : true))
    .sort((left, right) => right.updatedAt.localeCompare(left.updatedAt))
    .slice(0, limit);
}

const server = createServer(async (request, response) => {
  if (!request.url) {
    notFound(response);
    return;
  }

  const url = new URL(request.url, `http://${request.headers.host ?? `${HOST}:${PORT}`}`);

  if (request.method === "GET" && url.pathname === "/health") {
    sendJson(response, 200, { status: true, items: tasks.size });
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

  if (request.method === "POST" && url.pathname === "/events") {
    try {
      const event = parseStatusEvent(await readJsonBody(request));
      sendJson(response, 202, mergeStatusEvent(event));
      return;
    } catch (error) {
      if (error instanceof HttpError) {
        sendJson(response, error.statusCode, { error: error.message });
        return;
      }

      sendJson(response, 400, { error: error instanceof Error ? error.message : String(error) });
      return;
    }
  }

  if (request.method === "GET" && url.pathname === "/tasks") {
    sendJson(response, 200, { items: listTasks(url) });
    return;
  }

  if (request.method === "GET" && url.pathname.startsWith("/tasks/")) {
    const statusId = url.pathname.slice("/tasks/".length);
    const task = tasks.get(statusId);
    if (!task) {
      notFound(response);
      return;
    }

    sendJson(response, 200, task);
    return;
  }

  notFound(response);
});

server.listen(PORT, HOST, () => {
  console.log(JSON.stringify({ status: "listening", host: HOST, port: PORT }));
});
