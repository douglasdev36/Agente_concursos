import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeBanca, analyzeEdital, analyzeProva, analyzeProvaFigures, createUser, generateQuestions, generateQuestionsWithImages } from "../api";
import { loadState, saveState } from "../storage";
import type { AnaliseBanca, AnaliseProva, BlocoQuestoes, Edital, ListaQuestoes, Questao } from "../types";

const BANCA_PRESETS = [
  "Cebraspe (CESPE)",
  "FGV – Fundação Getulio Vargas",
  "FCC – Fundação Carlos Chagas",
  "Fundação Cesgranrio",
  "Vunesp",
  "IBFC",
  "Quadrix",
  "IBADE",
  "AOCP",
  "IADES",
  "Instituto Acesso",
  "Fundep (GV-concursos)",
  "AVANÇA SP",
  "CONSULPLAN",
  "IDECAN",
  "Instituto AOCP",
  "Legalle Concursos",
  "FAUEL",
  "FEPESE",
  "FUNCAB",
  "FUMARC",
  "Instituto Verbena",
  "OBJETIVA",
  "SELECON",
  "UPENET/IAUPE",
  "COVEST-COPSET"
] as const;

export default function ConfigPage() {
  const navigate = useNavigate();
  const initial = loadState();
  const [nomeBanca, setNomeBanca] = useState("");
  const [bancaPreset, setBancaPreset] = useState<string>("");
  const [editalText, setEditalText] = useState("");
  const [editalFile, setEditalFile] = useState<File | null>(null);
  const [provaText, setProvaText] = useState("");
  const [provaFile, setProvaFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [resultEdital, setResultEdital] = useState<Edital | null>(initial.edital || null);
  const [resultBanca, setResultBanca] = useState<AnaliseBanca | null>(initial.analise_banca || null);
  const [resultProva, setResultProva] = useState<AnaliseProva | null>(initial.analise_prova || null);
  const [provaFigurasRatio, setProvaFigurasRatio] = useState<number>(initial.prova_figuras_ratio || 0);
  const [provaFigurasPool, setProvaFigurasPool] = useState<string[]>(initial.prova_figuras_pool || []);
  const [error, setError] = useState<string | null>(null);
  const [novoEmail, setNovoEmail] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  const [msgUser, setMsgUser] = useState<string | null>(null);

  const [simDificuldade, setSimDificuldade] = useState<"Fácil" | "Médio" | "Difícil">("Médio");
  const [simAlternativas, setSimAlternativas] = useState(5);

  const [qtdMat, setQtdMat] = useState(0);
  const [qtdPort, setQtdPort] = useState(0);

  const [matMateriaSel, setMatMateriaSel] = useState<string>("");
  const [portMateriaSel, setPortMateriaSel] = useState<string>("");

  type EspItem = {
    id: string;
    quantidade: number;
    materiaSel: string;
    materiaManual: string;
    assuntoSel: string;
    assuntoManual: string;
  };

  const [espItens, setEspItens] = useState<EspItem[]>([
    {
      id: crypto.randomUUID(),
      quantidade: 0,
      materiaSel: "",
      materiaManual: "",
      assuntoSel: "__geral__",
      assuntoManual: ""
    }
  ]);

  const [gerandoSimulado, setGerandoSimulado] = useState(false);
  const [simMsg, setSimMsg] = useState<string | null>(null);
  const [simError, setSimError] = useState<string | null>(null);

  function addEspItem() {
    setEspItens((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        quantidade: 0,
        materiaSel: "",
        materiaManual: "",
        assuntoSel: "__geral__",
        assuntoManual: ""
      }
    ]);
  }

  function removeEspItem(id: string) {
    setEspItens((prev) => prev.filter((x) => x.id !== id));
  }

  function updateEspItem(id: string, patch: Partial<EspItem>) {
    setEspItens((prev) => prev.map((x) => (x.id === id ? { ...x, ...patch } : x)));
  }

  useEffect(() => {
    if (!resultEdital) return;
    const materias = resultEdital.materias.map((m) => m.nome);
    const findBy = (needle: string) =>
      materias.find((m) => m.toLowerCase().includes(needle.toLowerCase())) || "";

    if (!matMateriaSel) setMatMateriaSel(findBy("matem") || findBy("racioc") || "");
    if (!portMateriaSel) setPortMateriaSel(findBy("portug") || findBy("língua") || findBy("lingua") || "");
    setEspItens((prev) => {
      const next = prev.map((x) => ({ ...x }));
      const fallback = materias.find((m) => m !== matMateriaSel && m !== portMateriaSel) || "";
      for (const item of next) {
        if (!item.materiaSel) item.materiaSel = fallback;
      }
      return next;
    });
  }, [resultEdital]);

  const materiasDoEdital = useMemo(() => (resultEdital ? resultEdital.materias.map((m) => m.nome) : []), [resultEdital]);

  function assuntosPorMateria(nome: string): string[] {
    if (!resultEdital) return [];
    const mat = resultEdital.materias.find((m) => m.nome === nome);
    return (mat?.assuntos || []).map((a) => a.nome);
  }

  const totalSimulado = useMemo(() => {
    const esp = espItens.reduce((acc, it) => acc + (Number(it.quantidade) || 0), 0);
    return (Number(qtdMat) || 0) + (Number(qtdPort) || 0) + esp;
  }, [qtdMat, qtdPort, espItens]);

  async function onAnalyze() {
    setError(null);
    setMsgUser(null);
    setSimMsg(null);
    setSimError(null);
    setLoading(true);
    try {
      const erros: string[] = [];

      let edital: Edital | null = null;
      let banca: AnaliseBanca | null = null;
      let prova: AnaliseProva | null = null;

      try {
        edital = await analyzeEdital(editalText || undefined, editalFile || undefined);
        setResultEdital(edital);
        saveState({ edital });
      } catch (e: any) {
        erros.push(`Edital: ${e?.message || "erro"}`);
      }

      if (nomeBanca.trim()) {
        try {
          banca = await analyzeBanca(nomeBanca.trim());
          setResultBanca(banca);
          saveState({ analise_banca: banca });
        } catch (e: any) {
          erros.push(`Banca: ${e?.message || "erro"}`);
        }
      } else {
        setResultBanca(null);
        saveState({ analise_banca: null });
      }

      if (provaText.trim() || provaFile) {
        try {
          prova = await analyzeProva(provaText || undefined, provaFile || undefined);
          setResultProva(prova);
          saveState({ analise_prova: prova });

          if (provaFile && provaFile.name.toLowerCase().endsWith(".pdf")) {
            try {
              const figs = await analyzeProvaFigures(provaFile);
              setProvaFigurasRatio(Number(figs.ratio) || 0);
              setProvaFigurasPool(Array.isArray(figs.figuras) ? figs.figuras : []);
              saveState({
                prova_figuras_ratio: Number(figs.ratio) || 0,
                prova_figuras_pool: Array.isArray(figs.figuras) ? figs.figuras : []
              });
            } catch (e: any) {
              setProvaFigurasRatio(0);
              setProvaFigurasPool([]);
              saveState({ prova_figuras_ratio: 0, prova_figuras_pool: [] });
              erros.push(`Figuras da prova: ${e?.message || "erro"}`);
            }
          }
        } catch (e: any) {
          erros.push(`Prova: ${e?.message || "erro"}`);
        }
      } else {
        setResultProva(null);
        saveState({ analise_prova: null });
        setProvaFigurasRatio(0);
        setProvaFigurasPool([]);
        saveState({ prova_figuras_ratio: 0, prova_figuras_pool: [] });
      }

      if (erros.length) setError(erros.join(" | "));
    } catch (err: any) {
      setError(err?.message || "Erro ao analisar");
    } finally {
      setLoading(false);
    }
  }

  async function gerarParaMateria(materiaNome: string, assuntos: Array<{ nome: string }>, total: number): Promise<Questao[]> {
    const calls: Array<Promise<ListaQuestoes>> = [];
    if (!assuntos.length) {
      calls.push(
        generateQuestions({
          materia: materiaNome,
          assunto: "Geral",
          quantidade: total,
          dificuldade: simDificuldade,
          nivel_ensino: null,
          num_alternativas: simAlternativas,
          incluir_texto_base: false,
          analise_banca: resultBanca,
          analise_prova: resultProva,
          edital: resultEdital
        })
      );
    } else {
      const base = Math.floor(total / assuntos.length);
      const rem = total % assuntos.length;
      for (let i = 0; i < assuntos.length; i++) {
        const qtd = base + (i < rem ? 1 : 0);
        if (qtd <= 0) continue;
        calls.push(
          generateQuestions({
            materia: materiaNome,
            assunto: assuntos[i].nome,
            quantidade: qtd,
            dificuldade: simDificuldade,
            nivel_ensino: null,
            num_alternativas: simAlternativas,
            incluir_texto_base: false,
            analise_banca: resultBanca,
            analise_prova: resultProva,
            edital: resultEdital
          })
        );
      }
    }

    const results = await Promise.all(calls);
    const flat = results.flatMap((r) => r.questoes || []);
    return flat.map((q, idx) => ({ ...q, numero: idx + 1 }));
  }

  async function onGerarSimulado() {
    setSimMsg(null);
    setSimError(null);
    if (!resultEdital) {
      setSimError("Analise o edital primeiro.");
      return;
    }
    if (totalSimulado <= 0) {
      setSimError("Informe a quantidade de questões por matéria.");
      return;
    }
    setGerandoSimulado(true);
    try {
      const erros: string[] = [];
      const novos: BlocoQuestoes[] = [];
      const pool = [...(provaFigurasPool || [])];
      const ratio = Number(provaFigurasRatio) || 0;

      const jobs: Array<{
        categoria: string;
        materia: string;
        assunto: string;
        quantidade: number;
      }> = [];

      if (qtdMat > 0 && matMateriaSel) jobs.push({ categoria: "Matemática", materia: matMateriaSel, assunto: "Geral", quantidade: qtdMat });
      if (qtdPort > 0 && portMateriaSel) jobs.push({ categoria: "Português", materia: portMateriaSel, assunto: "Geral", quantidade: qtdPort });

      for (const it of espItens) {
        const qtd = Number(it.quantidade || 0);
        if (!qtd || qtd <= 0) continue;
        const materia = it.materiaSel === "__manual__" ? it.materiaManual.trim() : it.materiaSel;
        if (!materia) throw new Error("Informe a matéria das específicas.");

        let assunto = "Geral";
        if (it.assuntoSel === "__manual__") assunto = it.assuntoManual.trim() || "Geral";
        else if (it.assuntoSel === "__geral__") assunto = "Geral";
        else assunto = it.assuntoSel;

        jobs.push({ categoria: "Específicas", materia, assunto, quantidade: qtd });
      }

      async function dataUrlToFile(dataUrl: string, filename: string): Promise<File> {
        const resp = await fetch(dataUrl);
        const blob = await resp.blob();
        const type = blob.type || "image/png";
        return new File([blob], filename, { type });
      }

      for (const j of jobs) {
        try {
          const permiteImagem = j.categoria !== "Português";
          const alvoImg = permiteImagem && ratio > 0 ? Math.round(j.quantidade * ratio) : 0;
          const qtdImg = Math.max(0, Math.min(alvoImg, pool.length, j.quantidade));

          const questoes: Questao[] = [];
          const figurasPatch: Record<string, string> = {};

          if (qtdImg > 0) {
            const escolhidas = pool.splice(0, qtdImg);
            const files = await Promise.all(escolhidas.map((d, i) => dataUrlToFile(d, `fig-${Date.now()}-${i}.png`)));
            const listaImg = await generateQuestionsWithImages({
              materia: j.materia,
              assunto: j.assunto,
              dificuldade: simDificuldade,
              num_alternativas: simAlternativas,
              images: files,
              analise_banca: resultBanca,
              analise_prova: resultProva,
              edital: resultEdital
            });

            for (let i = 0; i < (listaImg.questoes || []).length; i++) {
              const key = crypto.randomUUID();
              figurasPatch[key] = escolhidas[i];
              (listaImg.questoes[i] as any).figura_key = key;
            }
            questoes.push(...(listaImg.questoes || []));
          }

          const restante = j.quantidade - qtdImg;
          if (restante > 0) {
            const lista = await generateQuestions({
              materia: j.materia,
              assunto: j.assunto,
              quantidade: restante,
              dificuldade: simDificuldade,
              nivel_ensino: null,
              num_alternativas: simAlternativas,
              incluir_texto_base: false,
              analise_banca: resultBanca,
              analise_prova: resultProva,
              edital: resultEdital
            });
            questoes.push(...(lista.questoes || []));
          }

          const renum = questoes.map((q, idx) => ({ ...q, numero: idx + 1 }));
          if (!questoes.length) continue;
          const label = j.assunto && j.assunto !== "Geral" ? `🎯 ${j.categoria} (${j.materia}) — ${j.assunto}` : `🎯 ${j.categoria} (${j.materia})`;
          const st = loadState();
          const figuras = { ...(st.figuras || {}), ...figurasPatch };
          saveState({ figuras });
          novos.push({
            label,
            dificuldade: `${simDificuldade} • ${simAlternativas} alts`,
            questoes: renum
          });
        } catch (e: any) {
          erros.push(`${j.categoria}: ${e?.message || "erro"}`);
        }
      }

      if (novos.length) {
        const st = loadState();
        const blocos = st.blocos || [];
        saveState({ blocos: [...blocos, ...novos] });
        setSimMsg(`Simulado atualizado: ${novos.length} bloco(s) adicionado(s).`);
        navigate("/simulado");
      }

      if (erros.length) setSimError(erros.join(" | "));
    } finally {
      setGerandoSimulado(false);
    }
  }

  async function onCreateUser() {
    setError(null);
    setMsgUser(null);
    setLoading(true);
    try {
      await createUser(novoEmail, novaSenha, false);
      setMsgUser("Usuário criado com sucesso.");
      setNovoEmail("");
      setNovaSenha("");
    } catch (err: any) {
      setError(err?.message || "Erro ao criar usuário");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h2>Configuração</h2>
      <div className="muted">Analisa edital, banca e prova de referência e salva no seu navegador.</div>
      <div className="hr" />

      <div className="row">
        <div className="col">
          <label>Banca (opcional)</label>
          <select
            value={bancaPreset}
            onChange={(e) => {
              const v = e.target.value;
              setBancaPreset(v);
              if (v === "__manual__") setNomeBanca("");
              else setNomeBanca(v);
            }}
          >
            <option value="">── Selecione uma banca ──</option>
            {BANCA_PRESETS.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
            <option value="__manual__">── Outra (digitar manualmente) ──</option>
          </select>
          {bancaPreset !== "__manual__" ? (
            <>
              <div style={{ height: 10 }} />
              <button
                type="button"
                onClick={() => {
                  setBancaPreset("__manual__");
                  setNomeBanca("");
                }}
                style={{ width: "auto" }}
              >
                Adicionar banca manualmente
              </button>
            </>
          ) : null}
          {bancaPreset === "__manual__" ? (
            <>
              <div style={{ height: 10 }} />
              <input value={nomeBanca} onChange={(e) => setNomeBanca(e.target.value)} placeholder="Ex: COPS-UEL, Movens, Instituto Quadrix..." />
              <div style={{ height: 10 }} />
              <button
                type="button"
                onClick={() => {
                  setBancaPreset("");
                  setNomeBanca("");
                }}
                style={{ width: "auto" }}
              >
                Voltar para lista
              </button>
            </>
          ) : null}
        </div>
      </div>

      <div className="hr" />

      <div className="row">
        <div className="col">
          <h3>Edital</h3>
          <div className="muted">Cole o conteúdo programático ou envie PDF/TXT.</div>
          <textarea value={editalText} onChange={(e) => setEditalText(e.target.value)} />
          <div style={{ height: 10 }} />
          <input type="file" accept=".pdf,.txt" onChange={(e) => setEditalFile(e.target.files?.[0] || null)} />
        </div>
        <div className="col">
          <h3>Prova de referência (opcional)</h3>
          <div className="muted">Cole o texto da prova ou envie PDF/TXT.</div>
          <textarea value={provaText} onChange={(e) => setProvaText(e.target.value)} />
          <div style={{ height: 10 }} />
          <input type="file" accept=".pdf,.txt" onChange={(e) => setProvaFile(e.target.files?.[0] || null)} />
        </div>
      </div>

      <div className="hr" />

      <button onClick={onAnalyze} disabled={loading}>
        {loading ? "Analisando..." : "Analisar e preparar estudo"}
      </button>

      {error ? (
        <div className="muted" style={{ marginTop: 12, color: "#fca5a5" }}>
          {error}
        </div>
      ) : null}
      {msgUser ? (
        <div className="muted" style={{ marginTop: 12, color: "#6ee7b7" }}>
          {msgUser}
        </div>
      ) : null}

      <div className="hr" />

      <div className="row">
        <div className="col">
          <h3>Resumo</h3>
          <div>
            <span className="pill">{resultEdital ? "Edital OK" : "Edital pendente"}</span>
            <span className="pill">{resultBanca ? "Banca OK" : "Banca opcional"}</span>
            <span className="pill">{resultProva ? "Prova OK" : "Prova opcional"}</span>
          </div>
        </div>
        <div className="col">
          {resultEdital ? (
            <div className="muted">
              Matérias identificadas: <strong style={{ color: "#e2e8f0" }}>{resultEdital.materias.length}</strong>
            </div>
          ) : (
            <div className="muted">Nenhum edital analisado ainda.</div>
          )}
        </div>
      </div>

      <div className="hr" />

      {resultEdital ? (
        <>
          <h3>Depois da análise: mandar questões para o simulado</h3>
          <div className="muted">
            Depois que o edital e a prova de referência forem analisados (e banca opcional), você escolhe quantas questões quer de Matemática, Português e Específicas. Você pode escolher as específicas pelo edital ou digitar manualmente (ex.: diagramas elétricos).
          </div>
          <div style={{ height: 10 }} />
          <div className="row">
            <div className="col">
              <label>Dificuldade</label>
              <select value={simDificuldade} onChange={(e) => setSimDificuldade(e.target.value as any)}>
                <option value="Fácil">Fácil</option>
                <option value="Médio">Médio</option>
                <option value="Difícil">Difícil</option>
              </select>
            </div>
            <div className="col">
              <label>Alternativas</label>
              <select value={simAlternativas} onChange={(e) => setSimAlternativas(Number(e.target.value))}>
                <option value={4}>4 (A-D)</option>
                <option value={5}>5 (A-E)</option>
              </select>
            </div>
            <div className="col">
              <label>Total</label>
              <input value={totalSimulado} disabled />
            </div>
          </div>

          <div style={{ height: 10 }} />

          <div className="row">
            <div className="col">
              <label>Matemática (qtd.)</label>
              <input type="number" min={0} max={50} value={qtdMat} onChange={(e) => setQtdMat(Number(e.target.value))} />
              <div style={{ height: 10 }} />
              <label>Matéria (do edital)</label>
              <select value={matMateriaSel} onChange={(e) => setMatMateriaSel(e.target.value)}>
                <option value="">Selecione</option>
                {materiasDoEdital.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>

            <div className="col">
              <label>Português (qtd.)</label>
              <input type="number" min={0} max={50} value={qtdPort} onChange={(e) => setQtdPort(Number(e.target.value))} />
              <div style={{ height: 10 }} />
              <label>Matéria (do edital)</label>
              <select value={portMateriaSel} onChange={(e) => setPortMateriaSel(e.target.value)}>
                <option value="">Selecione</option>
                {materiasDoEdital.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>

            <div className="col">
              <label>Específicas</label>
              <div className="muted">Adicione um ou mais assuntos específicos com quantidades separadas.</div>
              <div style={{ height: 10 }} />
              {espItens.map((it, idx) => {
                const assuntos = it.materiaSel && it.materiaSel !== "__manual__" ? assuntosPorMateria(it.materiaSel) : [];
                return (
                  <div key={it.id} className="card" style={{ marginTop: idx === 0 ? 0 : 12 }}>
                    <div className="row">
                      <div className="col">
                        <label>Qtd.</label>
                        <input
                          type="number"
                          min={0}
                          max={50}
                          value={it.quantidade}
                          onChange={(e) => updateEspItem(it.id, { quantidade: Number(e.target.value) })}
                        />
                      </div>
                      <div className="col">
                        <label>Matéria</label>
                        <select
                          value={it.materiaSel}
                          onChange={(e) =>
                            updateEspItem(it.id, {
                              materiaSel: e.target.value,
                              assuntoSel: "__geral__",
                              assuntoManual: ""
                            })
                          }
                        >
                          <option value="">Selecione</option>
                          {materiasDoEdital.map((m) => (
                            <option key={m} value={m}>
                              {m}
                            </option>
                          ))}
                          <option value="__manual__">Manual</option>
                        </select>
                        {it.materiaSel === "__manual__" ? (
                          <>
                            <div style={{ height: 10 }} />
                            <input
                              value={it.materiaManual}
                              onChange={(e) => updateEspItem(it.id, { materiaManual: e.target.value })}
                              placeholder="Ex.: Manutenção Elétrica"
                            />
                          </>
                        ) : null}
                      </div>
                      <div className="col">
                        <label>Assunto</label>
                        <select value={it.assuntoSel} onChange={(e) => updateEspItem(it.id, { assuntoSel: e.target.value })}>
                          <option value="__geral__">Geral</option>
                          {assuntos.map((a) => (
                            <option key={a} value={a}>
                              {a}
                            </option>
                          ))}
                          <option value="__manual__">Manual</option>
                        </select>
                        {it.assuntoSel === "__manual__" ? (
                          <>
                            <div style={{ height: 10 }} />
                            <input
                              value={it.assuntoManual}
                              onChange={(e) => updateEspItem(it.id, { assuntoManual: e.target.value })}
                              placeholder="Ex.: diagramas elétricos, unifilar, trifilar..."
                            />
                          </>
                        ) : null}
                      </div>
                    </div>
                    {espItens.length > 1 ? (
                      <>
                        <div style={{ height: 10 }} />
                        <button type="button" onClick={() => removeEspItem(it.id)} style={{ width: "auto" }}>
                          Remover
                        </button>
                      </>
                    ) : null}
                  </div>
                );
              })}
              <div style={{ height: 10 }} />
              <button type="button" onClick={addEspItem} style={{ width: "auto" }}>
                Adicionar assunto específico
              </button>
            </div>
          </div>

          <div style={{ height: 10 }} />
          <button disabled={loading || gerandoSimulado || totalSimulado <= 0} onClick={onGerarSimulado}>
            {gerandoSimulado ? "Gerando..." : "Gerar e enviar para o simulado"}
          </button>

          {simError ? (
            <div className="muted" style={{ marginTop: 12, color: "#fca5a5" }}>
              {simError}
            </div>
          ) : null}
          {simMsg ? (
            <div className="muted" style={{ marginTop: 12, color: "#6ee7b7" }}>
              {simMsg}
            </div>
          ) : null}

          <div className="hr" />
        </>
      ) : null}

      <h3>Usuários</h3>
      <div className="muted">Crie outros logins (somente admin).</div>
      <div style={{ height: 10 }} />
      <div className="row">
        <div className="col">
          <label>Novo email</label>
          <input value={novoEmail} onChange={(e) => setNovoEmail(e.target.value)} />
        </div>
        <div className="col">
          <label>Nova senha</label>
          <input type="password" value={novaSenha} onChange={(e) => setNovaSenha(e.target.value)} />
        </div>
      </div>
      <div style={{ height: 10 }} />
      <button onClick={onCreateUser} disabled={loading || !novoEmail || !novaSenha}>
        {loading ? "Processando..." : "Criar usuário"}
      </button>
    </div>
  );
}
