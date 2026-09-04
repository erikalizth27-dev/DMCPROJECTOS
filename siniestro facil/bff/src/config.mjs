const production = process.env.NODE_ENV === "production";

function required(name) {
  const value = process.env[name]?.trim();
  if (!value) throw new Error(`Falta la variable ${name}`);
  return value;
}

export function loadConfig() {
  const backendUrl = required("BACKEND_URL").replace(/\/$/, "");
  return {
    port: Number(process.env.PORT || 8080),
    backendUrl,
    backendAudience: (process.env.BACKEND_AUDIENCE || backendUrl).replace(/\/$/, ""),
    frontendOrigin: production
      ? required("FRONTEND_ORIGIN")
      : (process.env.FRONTEND_ORIGIN || "http://localhost:5173"),
  };
}
