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
