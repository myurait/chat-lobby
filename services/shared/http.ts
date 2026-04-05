import type { IncomingMessage, ServerResponse } from "node:http";

export class HttpError extends Error {
  readonly statusCode: number;

  constructor(statusCode: number, message: string) {
    super(message);
    this.statusCode = statusCode;
  }
}

export function sendJson(response: ServerResponse, statusCode: number, payload: unknown) {
  response.statusCode = statusCode;
  response.setHeader("Content-Type", "application/json; charset=utf-8");
  response.end(JSON.stringify(payload));
}

export function notFound(response: ServerResponse) {
  sendJson(response, 404, { error: "Not found" });
}

export async function readJsonBody(request: IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = [];
  for await (const chunk of request) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }

  if (chunks.length === 0) {
    return {};
  }

  try {
    return JSON.parse(Buffer.concat(chunks).toString("utf-8"));
  } catch {
    throw new HttpError(400, "Request body must be valid JSON.");
  }
}

export function requireBearerToken(request: IncomingMessage, expectedToken: string) {
  if (!expectedToken) {
    return;
  }

  const authorization = request.headers.authorization;
  if (typeof authorization !== "string" || !authorization.startsWith("Bearer ")) {
    throw new HttpError(401, "Missing bearer token.");
  }

  const providedToken = authorization.slice("Bearer ".length).trim();
  if (providedToken === "" || providedToken !== expectedToken) {
    throw new HttpError(401, "Invalid bearer token.");
  }
}

export function requireTokenForNonLoopbackBind(serviceName: string, host: string, token: string) {
  const loopbackHosts = new Set(["127.0.0.1", "localhost", "::1"]);
  if (!loopbackHosts.has(host) && token.trim() === "") {
    throw new Error(`${serviceName} requires a bearer token when bound to a non-loopback host.`);
  }
}
