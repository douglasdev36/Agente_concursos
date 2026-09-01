import { useMemo, useState } from "react";
import { loadState, saveState } from "../storage";
import type { BlocoQuestoes, Questao } from "../types";

function score(respostas: Record<string, string>, blocos: BlocoQuestoes[]) {
  let acertos = 0;
  let erros = 0;
  for (const bloco of blocos) {
    for (const q of bloco.questoes) {
      const key = `${bloco.label}::${q.numero}`;
      const r = respostas[key];
      if (!r) continue;
      if (r.toUpperCase() === q.resposta_correta.toUpperCase()) acertos++;
      else erros++;
    }
  }
  return { acertos, erros };
}

export default function SimuladoPage() {
  const initial = loadState();
  const [blocos, setBlocos] = useState<BlocoQuestoes[]>(initial.blocos || []);
  const [respostas, setRespostas] = useState<Record<string, string>>(initial.respostas || {});
  const [mostrarGabarito, setMostrarGabarito] = useState(false);
  const figuras = initial.figuras || {};

  const stats = useMemo(() => score(respostas, blocos), [respostas, blocos]);

  function setResposta(blocoLabel: string, numero: number, value: string) {
    const key = `${blocoLabel}::${numero}`;
    const next = { ...respostas, [key]: value };
    setRespostas(next);
    saveState({ respostas: next });
  }

  function limparTudo() {
    setBlocos([]);
    setRespostas({});
    saveState({ blocos: [], respostas: {}, figuras: {} });
  }

  function renderQuestao(blocoLabel: string, q: Questao) {
    const key = `${blocoLabel}::${q.numero}`;
    const selected = respostas[key] || "";
    const gabarito = q.resposta_correta.toUpperCase();

    const acertou = selected && selected.toUpperCase() === gabarito;
    const figuraData = q.figura_key ? figuras[q.figura_key] : null;

    return (
      <div className="card" key={key} style={{ marginTop: 12 }}>
        <div className="row" style={{ alignItems: "center" }}>
          <div className="col">
            <strong>Questão {q.numero}</strong> <span className="pill">{q.dificuldade}</span>
          </div>
          <div className="col" style={{ textAlign: "right" }}>
            <span className="muted">{q.materia}</span>
          </div>
        </div>

        {q.texto_base ? (
          <div className="card" style={{ marginTop: 12, borderColor: "rgba(96,165,250,0.35)" }}>
            {q.titulo_texto_base ? <strong>{q.titulo_texto_base}</strong> : null}
            <div style={{ whiteSpace: "pre-wrap", marginTop: 8 }}>{q.texto_base}</div>
          </div>
        ) : null}

        {figuraData ? (
          <div style={{ marginTop: 12 }}>
            <img src={figuraData} style={{ width: "100%", borderRadius: 12 }} />
          </div>
        ) : null}

        <div style={{ whiteSpace: "pre-wrap", marginTop: 12 }}>{q.enunciado}</div>

        <div className="hr" />
        {q.alternativas.map((alt) => {
          const letra = alt.letra.toUpperCase();
          const checked = selected === letra;
          const isGabarito = letra === gabarito;

          let bg = "transparent";
          if (mostrarGabarito) {
            if (checked && isGabarito) bg = "rgba(52,211,153,0.15)";
            else if (isGabarito) bg = "rgba(52,211,153,0.10)";
            else if (checked) bg = "rgba(239,68,68,0.12)";
          }

          return (
            <label
              key={alt.letra}
              style={{
                display: "block",
                padding: "10px 12px",
                borderRadius: 10,
                border: "1px solid rgba(148,163,184,0.2)",
                marginBottom: 8,
                background: bg,
                cursor: "pointer"
              }}
            >
              <input
                type="radio"
                name={key}
                checked={checked}
                onChange={() => setResposta(blocoLabel, q.numero, letra)}
                style={{ marginRight: 8 }}
              />
              <strong>{letra})</strong> {alt.texto}
              {mostrarGabarito && isGabarito ? <span className="muted"> (gabarito)</span> : null}
            </label>
          );
        })}

        {mostrarGabarito ? (
          <>
            <div className="hr" />
            {selected ? (
              <div style={{ color: acertou ? "#6ee7b7" : "#fca5a5" }}>
                {acertou ? "Correta." : `Incorreta. Gabarito: ${gabarito}.`}
              </div>
            ) : (
              <div className="muted">Sem resposta marcada. Gabarito: {gabarito}.</div>
            )}
            <div className="hr" />
            <div className="muted">Explicação</div>
            <div style={{ whiteSpace: "pre-wrap", marginTop: 8 }}>{q.explicacao}</div>
          </>
        ) : null}
      </div>
    );
  }

  if (!blocos.length) {
    return (
      <div className="card">
        <h2>Simulado</h2>
        <div className="muted">Você ainda não adicionou questões. Gere em Configuração/Questões rápidas.</div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Simulado</h2>
      <div className="muted">
        Acertos: <strong>{stats.acertos}</strong> • Erros: <strong>{stats.erros}</strong>
      </div>
      <div className="hr" />

      <div className="row">
        <div className="col">
          <button onClick={() => setMostrarGabarito((v) => !v)}>
            {mostrarGabarito ? "Ocultar correção" : "Finalizar e corrigir"}
          </button>
        </div>
        <div className="col">
          <button onClick={limparTudo}>Limpar tudo</button>
        </div>
      </div>

      {blocos.map((b) => (
        <div key={b.label} style={{ marginTop: 20 }}>
          <div className="card" style={{ borderColor: "rgba(139,92,246,0.4)" }}>
            <strong>{b.label}</strong> <span className="pill">{b.dificuldade}</span>{" "}
            <span className="muted">({b.questoes.length} questão(ões))</span>
          </div>
          {b.questoes.map((q) => renderQuestao(b.label, q))}
        </div>
      ))}
    </div>
  );
}

