import { expect, test } from "@playwright/test";

const required = [
  "E2E_BASE_URL",
  "E2E_EMAIL",
  "E2E_PASSWORD",
  "E2E_CASE_ID",
] as const;

test("el asegurado consulta un caso con evidencia registrada", async ({ page }) => {
  for (const name of required) {
    if (!process.env[name]) {
      throw new Error(`Falta la variable ${name}`);
    }
  }

  const baseUrl = process.env.E2E_BASE_URL!;
  const email = process.env.E2E_EMAIL!;
  const password = process.env.E2E_PASSWORD!;
  const caseId = process.env.E2E_CASE_ID!;

  await page.goto(baseUrl);

  await page.getByLabel("Correo electrónico").fill(email);
  await page.getByLabel("Contraseña").fill(password);
  await page.getByRole("button", { name: "Ingresar" }).click();

  await expect(
    page.getByRole("button", { name: "Consultar mi caso" }),
  ).toBeVisible();

  await page.getByRole("button", { name: "Consultar mi caso" }).click();
  await page.getByLabel("Número de caso").fill(caseId);
  await page.getByRole("button", { name: "Consultar", exact: true }).click();

  await expect(page.getByText(`#${caseId}`, { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Historial del caso" })).toBeVisible();
  await expect(page.getByText(/evidencia registrada/i)).toBeVisible();
});
