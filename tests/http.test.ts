import test from "node:test";
import assert from "node:assert/strict";
import { requireBearerToken } from "../services/shared/http.ts";

function createRequest(authorization?: string) {
  return {
    headers: authorization ? { authorization } : {},
  } as Parameters<typeof requireBearerToken>[0];
}

test("requireBearerToken accepts matching bearer token", () => {
  assert.doesNotThrow(() => requireBearerToken(createRequest("Bearer secret-token"), "secret-token"));
});

test("requireBearerToken rejects missing bearer token when configured", () => {
  assert.throws(() => requireBearerToken(createRequest(), "secret-token"), /Missing bearer token/);
});

test("requireBearerToken rejects invalid bearer token", () => {
  assert.throws(() => requireBearerToken(createRequest("Bearer wrong"), "secret-token"), /Invalid bearer token/);
});
