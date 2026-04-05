import test from "node:test";
import assert from "node:assert/strict";
import { HttpError } from "../services/shared/http.ts";
import {
  normalizeKnowledgeQuery,
  parseDispatchRequest,
  routeRequest,
  type RoutingRules,
} from "../services/dispatcher/src/routing.ts";

const routingRules: RoutingRules = {
  workers: {
    knowledge: {
      explicitFields: ["query", "path"],
      keywords: ["検索", "spec"],
    },
    claude: {
      keywords: ["調査", "investigate"],
    },
    codex: {
      keywords: ["実装", "fix"],
    },
  },
  defaultWorker: "claude",
};

test("parseDispatchRequest rejects empty payload", () => {
  assert.throws(() => parseDispatchRequest({}), HttpError);
});

test("routeRequest prefers explicit knowledge fields", () => {
  const routed = routeRequest({ query: "ChatLobby" }, routingRules);
  assert.deepEqual(routed, { worker: "knowledge", reason: "explicit knowledge fields" });
});

test("routeRequest respects workerHint override", () => {
  const routed = routeRequest({ prompt: "実装して", workerHint: "claude" }, routingRules);
  assert.deepEqual(routed, { worker: "claude", reason: "workerHint override" });
});

test("routeRequest falls back to keyword match", () => {
  const routed = routeRequest({ prompt: "この不具合をfixして" }, routingRules);
  assert.equal(routed.worker, "codex");
  assert.match(routed.reason, /keyword match/);
});

test("normalizeKnowledgeQuery strips command words and keeps subject", () => {
  assert.equal(normalizeKnowledgeQuery("ChatLobby の仕様を検索して"), "ChatLobby");
});
