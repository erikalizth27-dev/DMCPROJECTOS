import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  retries: 1,
  use: {
    browserName: "chromium",
    headless: true,
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
});
