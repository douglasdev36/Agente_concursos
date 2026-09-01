import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { login } from "../api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as any)?.from || "/config";

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err?.message || "Erro ao logar");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h2>Login</h2>
      <div className="muted">Entre com seu email e senha (admin) para usar o sistema.</div>
      <div className="hr" />

      <form onSubmit={onSubmit}>
        <div className="row">
          <div className="col">
            <label>Email</label>
            <input value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div className="col">
            <label>Senha</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
        </div>
        <div className="hr" />
        <button disabled={loading || !email || !password}>{loading ? "Entrando..." : "Entrar"}</button>
        {error ? (
          <div className="muted" style={{ marginTop: 12, color: "#fca5a5" }}>
            {error}
          </div>
        ) : null}
      </form>
    </div>
  );
}

