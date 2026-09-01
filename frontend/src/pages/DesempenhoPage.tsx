import { loadState } from "../storage";
import type { BlocoQuestoes } from "../types";

function calc(blocos: BlocoQuestoes[], respostas: Record<string, string>) {
  let total = 0;
  let respondidas = 0;
  let acertos = 0;
  let erros = 0;

  for (const b of blocos) {
    for (const q of b.questoes) {
      total++;
      const key = `${b.label}::${q.numero}`;
      const r = respostas[key];
      if (!r) continue;
      respondidas++;
      if (r.toUpperCase() === q.resposta_correta.toUpperCase()) acertos++;
      else erros++;
    }
  }

  const pct = respondidas ? Math.round((acertos / respondidas) * 100) : 0;
  return { total, respondidas, acertos, erros, pct };
}

export default function DesempenhoPage() {
  const st = loadState();
  const blocos = st.blocos || [];
  const respostas = st.respostas || {};
  const { total, respondidas, acertos, erros, pct } = calc(blocos, respostas);

  return (
    <div className="card">
      <h2>Desempenho</h2>
      <div className="muted">Calculado a partir das respostas marcadas no Simulado.</div>
      <div className="hr" />

      <div className="row">
        <div className="col card">
          <div className="muted">Total de questões</div>
          <div style={{ fontSize: 28, fontWeight: 800 }}>{total}</div>
        </div>
        <div className="col card">
          <div className="muted">Respondidas</div>
          <div style={{ fontSize: 28, fontWeight: 800 }}>{respondidas}</div>
        </div>
        <div className="col card">
          <div className="muted">Acertos</div>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#6ee7b7" }}>{acertos}</div>
        </div>
        <div className="col card">
          <div className="muted">Erros</div>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#fca5a5" }}>{erros}</div>
        </div>
      </div>

      <div className="hr" />
      <div className="muted">Aproveitamento</div>
      <div style={{ fontSize: 34, fontWeight: 900 }}>{pct}%</div>
    </div>
  );
}

