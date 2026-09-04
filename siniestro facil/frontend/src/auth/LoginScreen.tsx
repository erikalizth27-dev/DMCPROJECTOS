import { FormEvent, useState } from "react";
import { useAuth } from "./AuthContext";
import { AuthenticationError } from "./identityPlatform";

export function LoginScreen() {
  const { signIn } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setBusy(true);

    try {
      await signIn(email.trim(), password);
    } catch (cause) {
      setError(
        cause instanceof AuthenticationError
          ? cause.message
          : "No fue posible iniciar sesión.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="login-shell">
      <section className="login-card" aria-labelledby="login-title">
        <span className="login-mark" aria-hidden="true">SF</span>
        <p className="eyebrow">Seguro Horizonte</p>
        <h1 id="login-title">Ingresa a Siniestro Fácil</h1>
        <p className="login-copy">Consulta o reporta un siniestro con tu cuenta registrada.</p>

        <form onSubmit={submit}>
          <label>
            Correo electrónico
            <input
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          <label>
            Contraseña
            <input
              type="password"
              autoComplete="current-password"
              required
              minLength={6}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>

          {error && <div className="notice error" role="alert">{error}</div>}

          <button className="primary-action" disabled={busy}>
            {busy ? "Ingresando…" : "Ingresar"}
          </button>
        </form>
      </section>
    </main>
  );
}
