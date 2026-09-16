import assert from "node:assert/strict";
import test from "node:test";
import {
  isAllowedApiPath,
  isAllowedOrigin,
  selectRequestHeaders,
} from "../src/app.mjs";
import { parseFrontendOrigins } from "../src/config.mjs";

test("solo admite la superficie /api/v1", () => {
  assert.equal(isAllowedApiPath("/api/v1/siniestros"), true);
  assert.equal(isAllowedApiPath("/admin"), false);
  assert.equal(isAllowedApiPath("/api/v10"), false);
});

test("acepta ambos orígenes productivos y rechaza otros", () => {
  const origins = parseFrontendOrigins(
    "https://frontend-6oegsjqmba-uc.a.run.app, https://frontend-112296734690.us-central1.run.app/",
  );

  assert.deepEqual(origins, [
    "https://frontend-6oegsjqmba-uc.a.run.app",
    "https://frontend-112296734690.us-central1.run.app",
  ]);
  assert.equal(
    isAllowedOrigin("https://frontend-6oegsjqmba-uc.a.run.app", origins),
    true,
  );
  assert.equal(
    isAllowedOrigin(
      "https://frontend-112296734690.us-central1.run.app",
      origins,
    ),
    true,
  );
  assert.equal(isAllowedOrigin("https://otro.example", origins), false);
});

test("elimina duplicados y rechaza una lista vacía", () => {
  assert.deepEqual(
    parseFrontendOrigins("https://frontend.example,https://frontend.example"),
    ["https://frontend.example"],
  );
  assert.throws(() => parseFrontendOrigins(" , "), /al menos un origen/);
});

test("no reenvía cookies ni cabeceras de infraestructura", () => {
  assert.deepEqual(
    selectRequestHeaders({
      authorization: "Bearer human",
      "content-type": "application/json",
      cookie: "session=secret",
      host: "attacker.example",
      "x-serverless-authorization": "Bearer attacker",
    }),
    {
      authorization: "Bearer human",
      "content-type": "application/json",
    },
  );
});
