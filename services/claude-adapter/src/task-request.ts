export type ClaudeTaskRequest = {
  prompt: string;
  workingDirectory?: string;
  permissionMode?: string;
  model?: string;
  appendSystemPrompt?: string;
  allowedTools?: string[];
};

export function parseClaudeTaskRequest(input: unknown, defaultPermissionMode: string): ClaudeTaskRequest {
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
        : defaultPermissionMode,
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

export function buildClaudeCommand(task: ClaudeTaskRequest, defaultPermissionMode: string): string[] {
  const command = ["-p", "--output-format", "json", "--permission-mode", task.permissionMode ?? defaultPermissionMode];

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
