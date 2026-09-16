const production = process.env.NODE_ENV === "production";

function required(name) {
  const value = process.env[name]?.trim();
  if (!value) throw new Error(`Falta la variable ${name}`);
  return value;
}

export function parseFrontendOrigins(value) {
  const origins = value
    .split(",")
    .map((origin) => origin.trim().replace(/\/$/, ""))
    .filter(Boolean);
  if (origins.length === 0) {
    throw new Error("FRONTEND_ORIGINS debe contener al menos un origen");
  }
  return [...new Set(origins)];
}

export function loadConfig() {
  const backendUrl = required("BACKEND_URL").replace(/\/$/, "");
  const configuredOrigins =
    process.env.FRONTEND_ORIGINS ||
    process.env.FRONTEND_ORIGIN ||
    (production ? "" : "http://localhost:5173");
  if (!configuredOrigins) {
    throw new Error("Falta la variable FRONTEND_ORIGINS");
  }
  return {
    port: Number(process.env.PORT || 8080),
    backendUrl,
    backendAudience: (process.env.BACKEND_AUDIENCE || backendUrl).replace(/\/$/, ""),
    frontendOrigins: parseFrontendOrigins(configuredOrigins),
  };
}
