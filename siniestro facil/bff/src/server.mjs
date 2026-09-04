import { createApp } from "./app.mjs";
import { loadConfig } from "./config.mjs";

const config = loadConfig();
createApp(config).listen(config.port, "0.0.0.0", () => {
  console.log(
    JSON.stringify({
      severity: "INFO",
      event: "bff_started",
      port: config.port,
    }),
  );
});
