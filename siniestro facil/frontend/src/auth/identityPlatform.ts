interface RefreshTokenResponse {
  expires_in: string;
  refresh_token: string;
  id_token: string;
  user_id: string;
}

interface IdentityPlatformResponse {
  idToken: string;
  refreshToken: string;
  expiresIn: string;
  localId: string;
  email: string;
}

export interface AuthSession {
  idToken: string;
  refreshToken: string;
  expiresAt: number;
  user: {
    id: string;
    email: string;
  };
}

export class AuthenticationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AuthenticationError";
  }
}

const apiKey = import.meta.env.VITE_IDENTITY_PLATFORM_API_KEY as string | undefined;

export async function signInWithEmail(
  email: string,
  password: string,
): Promise<AuthSession> {
  if (!apiKey) {
    throw new AuthenticationError("El acceso todavía no está configurado.");
  }

  const response = await fetch(
    `https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=${encodeURIComponent(apiKey)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email,
        password,
        returnSecureToken: true,
      }),
    },
  );

  if (!response.ok) {
    throw new AuthenticationError(
      response.status === 400
        ? "El correo o la contraseña no son válidos."
        : "No fue posible iniciar sesión. Intenta nuevamente.",
    );
  }

  const body = (await response.json()) as IdentityPlatformResponse;
  return {
    idToken: body.idToken,
    refreshToken: body.refreshToken,
    expiresAt: Date.now() + Number(body.expiresIn) * 1000,
    user: {
      id: body.localId,
      email: body.email,
    },
  };
}

export async function refreshAuthSession(
  session: AuthSession,
): Promise<AuthSession> {
  if (!apiKey) {
    throw new AuthenticationError("El acceso todavía no está configurado.");
  }

  const body = new URLSearchParams({
    grant_type: "refresh_token",
    refresh_token: session.refreshToken,
  });
  const response = await fetch(
    `https://securetoken.googleapis.com/v1/token?key=${encodeURIComponent(apiKey)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    },
  );

  if (!response.ok) {
    throw new AuthenticationError(
      "Tu sesión finalizó. Ingresa nuevamente para continuar.",
    );
  }

  const refreshed = (await response.json()) as RefreshTokenResponse;
  return {
    idToken: refreshed.id_token,
    refreshToken: refreshed.refresh_token,
    expiresAt: Date.now() + Number(refreshed.expires_in) * 1000,
    user: {
      id: refreshed.user_id,
      email: session.user.email,
    },
  };
}
