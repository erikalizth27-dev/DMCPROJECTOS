import assert from "node:assert/strict";
import test from "node:test";
import { isAllowedApiPath, selectRequestHeaders } from "../src/app.mjs";

test("solo admite la superficie /api/v1", () => {
  assert.equal(isAllowedApiPath("/api/v1/siniestros"), true);
  assert.equal(isAllowedApiPath("/admin"), false);
  assert.equal(isAllowedApiPath("/api/v10"), false);
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
