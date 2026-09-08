import { createContext, ReactNode, useContext, useEffect, useMemo, useState } from "react";
import { AuthSession, refreshAuthSession, signInWithEmail } from "./identityPlatform";

interface AuthContextValue {
  session: AuthSession | null;
  signIn(email: string, password: string): Promise<void>;
  signOut(): void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AuthSession | null>(null);

  useEffect(() => {
    if (!session) {
      return;
    }

    let cancelled = false;
    const refreshDelay = Math.max(
      session.expiresAt - Date.now() - 5 * 60 * 1000,
      0,
    );
    const timeoutId = window.setTimeout(async () => {
      try {
        const refreshed = await refreshAuthSession(session);
        if (!cancelled) {
          setSession(refreshed);
        }
      } catch {
        if (!cancelled) {
          setSession(null);
        }
      }
    }, refreshDelay);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [session]);

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      async signIn(email, password) {
        setSession(await signInWithEmail(email, password));
      },
      signOut() {
        setSession(null);
      },
    }),
    [session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth debe utilizarse dentro de AuthProvider");
  }
  return context;
}
