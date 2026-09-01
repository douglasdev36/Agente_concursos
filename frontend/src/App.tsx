import { useEffect, useState } from "react";
import { Navigate, Route, Routes, Link, useLocation, useNavigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import ConfigPage from "./pages/ConfigPage";
import RapidoPage from "./pages/RapidoPage";
import SimuladoPage from "./pages/SimuladoPage";
import DesempenhoPage from "./pages/DesempenhoPage";
import { clearState, clearToken, loadToken } from "./storage";

function RequireAuth({ children }: { children: JSX.Element }) {
  const token = loadToken();
  const location = useLocation();
  if (!token) return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  return children;
}

export default function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const [token, setToken] = useState<string | null>(loadToken());

  useEffect(() => {
    setToken(loadToken());
  }, [location.pathname]);

  function onLogout() {
    clearToken();
    clearState();
    setToken(null);
    navigate("/login", { replace: true });
  }

  return (
    <div className="container">
      <h1 className="title">ConcursoAI</h1>
      <div className="muted">Frontend React (Vercel) + API Python (Render)</div>

      <div className="nav">
        <Link to="/config">Configuração</Link>
        <Link to="/rapido">Questões rápidas</Link>
        <Link to="/simulado">Simulado</Link>
        <Link to="/desempenho">Desempenho</Link>
        {token ? (
          <button type="button" onClick={onLogout}>
            Sair
          </button>
        ) : null}
      </div>

      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/config"
          element={
            <RequireAuth>
              <ConfigPage />
            </RequireAuth>
          }
        />
        <Route
          path="/rapido"
          element={
            <RequireAuth>
              <RapidoPage />
            </RequireAuth>
          }
        />
        <Route
          path="/simulado"
          element={
            <RequireAuth>
              <SimuladoPage />
            </RequireAuth>
          }
        />
        <Route
          path="/desempenho"
          element={
            <RequireAuth>
              <DesempenhoPage />
            </RequireAuth>
          }
        />
        <Route path="/" element={<Navigate to="/config" replace />} />
        <Route path="*" element={<Navigate to="/config" replace />} />
      </Routes>
    </div>
  );
}
