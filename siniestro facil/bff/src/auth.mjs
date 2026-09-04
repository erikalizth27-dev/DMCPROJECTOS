import { applicationDefault, getApps, initializeApp } from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";

if (!getApps().length) {
  initializeApp({ credential: applicationDefault() });
}

export async function verifyHumanToken(authorization) {
  const match = /^Bearer\s+(.+)$/i.exec(authorization || "");
  if (!match) {
    const error = new Error("Token de usuario ausente");
    error.status = 401;
    throw error;
  }

  const decoded = await getAuth().verifyIdToken(match[1], true);
  for (const claim of ["actor_type", "role", "tenant_id"]) {
    if (!decoded[claim]) {
      const error = new Error(`Claim requerida ausente: ${claim}`);
      error.status = 403;
      throw error;
    }
  }
  return decoded;
}
