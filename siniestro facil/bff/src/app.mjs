import express from "express";
import { randomUUID } from "node:crypto";
import { verifyHumanToken } from "./auth.mjs";
import { getServerlessAuthorization } from "./cloudRun.mjs";

const METHODS = new Set(["GET", "POST", "PUT", "PATCH", "DELETE"]);
const FORWARDED_REQUEST_HEADERS = [
  "authorization",
  "content-type",
  "idempotency-key",
  "x-correlation-id",
];

export function isAllowedApiPath(path) {
  return path === "/api/v1" || path.startsWith("/api/v1/");
}

export function selectRequestHeaders(headers) {
  const selected = {};
  for (const name of FORWARDED_REQUEST_HEADERS) {
    const value = headers[name];
    if (typeof value === "string" && value) selected[name] = value;
  }
  return selected;
}

export function createApp(config, dependencies = {}) {
  const app = express();
  const verifyToken = dependencies.verifyToken || verifyHumanToken;
  const serverlessToken =
    dependencies.serverlessToken || getServerlessAuthorization;
  const request = dependencies.fetch || fetch;

  app.disable("x-powered-by");

  app.use((req, res, next) => {
    const origin = req.get("origin");
    if (origin === config.frontendOrigin) {
      res.set({
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Headers":
          "Authorization, Content-Type, Idempotency-Key, X-Correlation-ID",
        "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        Vary: "Origin",
      });
    }
    if (req.method === "OPTIONS") {
      return origin === config.frontendOrigin
        ? res.sendStatus(204)
        : res.status(403).json({ detail: "Origen no autorizado" });
    }
    next();
  });

  app.get("/health/live", (_req, res) => res.json({ status: "ok" }));
  app.get("/health/ready", (_req, res) =>
    res.json({ status: "ready", errors: [] }),
  );

  app.use(
    "/api/v1",
    express.raw({ type: () => true, limit: "2mb" }),
    async (req, res) => {
      const correlationId = req.get("x-correlation-id") || randomUUID();
      res.set("x-correlation-id", correlationId);

      try {
        if (!METHODS.has(req.method) || !isAllowedApiPath(req.originalUrl.split("?")[0])) {
          return res.status(405).json({ detail: "Operación no permitida" });
        }

        await verifyToken(req.get("authorization"));
        const serviceAuthorization = await serverlessToken(
          config.backendAudience,
        );
        const headers = selectRequestHeaders(req.headers);
        headers["x-correlation-id"] = correlationId;
        headers["x-serverless-authorization"] = serviceAuthorization;

        const upstream = await request(
          `${config.backendUrl}${req.originalUrl}`,
          {
            method: req.method,
            headers,
            body: ["GET", "HEAD"].includes(req.method)
              ? undefined
              : req.body,
            redirect: "manual",
          },
        );

        res.status(upstream.status);
        const contentType = upstream.headers.get("content-type");
        if (contentType) res.set("content-type", contentType);
        const upstreamCorrelation = upstream.headers.get("x-correlation-id");
        if (upstreamCorrelation) {
          res.set("x-correlation-id", upstreamCorrelation);
        }
        res.send(Buffer.from(await upstream.arrayBuffer()));
      } catch (error) {
        const status =
          Number.isInteger(error.status) ? error.status : 502;
        console.error(
          JSON.stringify({
            severity: status >= 500 ? "ERROR" : "WARNING",
            event: "bff_request_failed",
            correlation_id: correlationId,
            status,
            message: error.message,
          }),
        );
        res.status(status).json({
          detail: status >= 500 ? "No fue posible contactar el backend" : error.message,
          correlation_id: correlationId,
        });
      }
    },
  );

  app.use((_req, res) => res.status(404).json({ detail: "Ruta no encontrada" }));
  return app;
}
