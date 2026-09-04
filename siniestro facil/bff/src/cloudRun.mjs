import { GoogleAuth } from "google-auth-library";

const auth = new GoogleAuth();

export async function getServerlessAuthorization(audience) {
  const client = await auth.getIdTokenClient(audience);
  const headers = await client.getRequestHeaders();
  const authorization = headers.get
    ? headers.get("authorization")
    : headers.authorization || headers.Authorization;

  if (!authorization) throw new Error("No se pudo obtener el token de servicio");
  return authorization;
}
