export type CodexTaskRequest = {
  prompt: string;
  workingDirectory?: string;
  model?: string;
  sandboxMode?: "read-only" | "workspace-write" | "danger-full-access";
  skipGitRepoCheck?: boolean;
  bypassApprovalsAndSandbox?: boolean;
};

export function parseCodexTaskRequest(
  input: unknown,
  defaultSandboxMode: CodexTaskRequest["sandboxMode"],
  defaultSkipGitRepoCheck: boolean,
  defaultBypassApprovals: boolean,
): CodexTaskRequest {
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
      : defaultSandboxMode;

  return {
    prompt: request.prompt,
    workingDirectory:
      typeof request.workingDirectory === "string" && request.workingDirectory.trim() !== ""
        ? request.workingDirectory
        : process.cwd(),
    model: typeof request.model === "string" && request.model.trim() !== "" ? request.model : undefined,
    sandboxMode,
    skipGitRepoCheck:
      typeof request.skipGitRepoCheck === "boolean" ? request.skipGitRepoCheck : defaultSkipGitRepoCheck,
    bypassApprovalsAndSandbox:
      typeof request.bypassApprovalsAndSandbox === "boolean"
        ? request.bypassApprovalsAndSandbox
        : defaultBypassApprovals,
  };
}

export function buildCodexCommand(task: CodexTaskRequest): string[] {
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
