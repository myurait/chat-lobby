export type WorkerName = "claude" | "codex" | "knowledge";
export type StatusState = "running" | "succeeded" | "failed";
export type ApprovalState = "not_required" | "may_require_approval" | "bypassed" | "unknown";

export type StatusEvent = {
  statusId?: string;
  taskId: string;
  worker: WorkerName;
  state: StatusState;
  title?: string;
  prompt?: string;
  workingDirectory?: string;
  currentStep?: string;
  lastAction?: string;
  approvalState?: ApprovalState;
  resultSummary?: string;
  error?: string;
  createdAt?: string;
  completedAt?: string;
  metadata?: Record<string, unknown>;
};

export type StatusRecord = StatusEvent & {
  statusId: string;
  updatedAt: string;
};

export function buildStatusId(worker: WorkerName, taskId: string): string {
  return `${worker}:${taskId}`;
}

export async function publishStatusEvent(baseUrl: string, token: string, event: StatusEvent): Promise<void> {
  if (!baseUrl) {
    return;
  }

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${baseUrl}/events`, {
    method: "POST",
    headers,
    body: JSON.stringify(event),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(`status store rejected event (${response.status}): ${message}`);
  }
}
