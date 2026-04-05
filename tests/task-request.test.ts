import test from "node:test";
import assert from "node:assert/strict";
import { buildClaudeCommand, parseClaudeTaskRequest } from "../services/claude-adapter/src/task-request.ts";
import { buildCodexCommand, parseCodexTaskRequest } from "../services/codex-adapter/src/task-request.ts";

test("parseClaudeTaskRequest applies defaults and filters allowed tools", () => {
  const request = parseClaudeTaskRequest(
    {
      prompt: "Implement feature",
      allowedTools: ["Edit", "", 3, "Read"],
    },
    "acceptEdits",
  );

  assert.equal(request.permissionMode, "acceptEdits");
  assert.deepEqual(request.allowedTools, ["Edit", "Read"]);
});

test("buildClaudeCommand includes optional flags in stable order", () => {
  const command = buildClaudeCommand(
    {
      prompt: "Investigate",
      permissionMode: "acceptEdits",
      model: "sonnet",
      appendSystemPrompt: "Follow rules",
      allowedTools: ["Read", "Edit"],
    },
    "acceptEdits",
  );

  assert.deepEqual(command, [
    "-p",
    "--output-format",
    "json",
    "--permission-mode",
    "acceptEdits",
    "--model",
    "sonnet",
    "--append-system-prompt",
    "Follow rules",
    "--allowedTools",
    "Read,Edit",
    "Investigate",
  ]);
});

test("parseCodexTaskRequest applies configured defaults", () => {
  const request = parseCodexTaskRequest({ prompt: "Fix bug" }, "workspace-write", true, false);

  assert.equal(request.sandboxMode, "workspace-write");
  assert.equal(request.skipGitRepoCheck, true);
  assert.equal(request.bypassApprovalsAndSandbox, false);
});

test("buildCodexCommand uses sandbox unless bypass is explicitly enabled", () => {
  const safeCommand = buildCodexCommand({
    prompt: "Fix bug",
    sandboxMode: "workspace-write",
    skipGitRepoCheck: true,
    bypassApprovalsAndSandbox: false,
  });
  assert.deepEqual(safeCommand, ["exec", "--json", "--skip-git-repo-check", "--sandbox", "workspace-write", "Fix bug"]);

  const bypassCommand = buildCodexCommand({
    prompt: "Fix bug",
    skipGitRepoCheck: true,
    bypassApprovalsAndSandbox: true,
  });
  assert.deepEqual(bypassCommand, ["exec", "--json", "--skip-git-repo-check", "--dangerously-bypass-approvals-and-sandbox", "Fix bug"]);
});
