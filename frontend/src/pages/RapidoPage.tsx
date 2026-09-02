import { useMemo, useState } from "react";
import { completeQuestion, generateQuestions, generateQuestionsWithImages } from "../api";
import { loadState, saveState } from "../storage";
import type { BlocoQuestoes, ListaQuestoes } from "../types";

function splitEnunciados(raw: string) {
  const normalized = raw.replace(/\r\n/g, "\n").trim();
  if (!normalized) return [];
  if (normalized.includes("\n\n")) {
    return normalized
      .split("\n\n")
      .map((b) => b.trim())
      .filter(Boolean);
  }

  const parts = normalized
    .split(/\n(?=(?:Quest[aã]o\s*\d+|\d{1,3}[).\-])\s+)/i)
    .map((b) => b.trim())
    .filter(Boolean);

  if (parts.length <= 1) return [normalized];

  return parts.map((p) => p.replace(/^(?:Quest[aã]o\s*\d+|\d{1,3}[).\-])\s+/i, "").trim()).filter(Boolean);
}

async function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export default function RapidoPage() {
  const st = loadState();
  const [modo, setModo] = useState<"gerar" | "completar">("gerar");
  const [materia, setMateria] = useState("");
  const [assunto, setAssunto] = useState("");
  const [questoesExemplo, setQuestoesExemplo] = useState("");
  const [qtd, setQtd] = useState(5);
  const [nivel, setNivel] = useState<"Fundamental" | "Médio" | "Superior">("Superior");
  const [dificuldade, setDificuldade] = useState("Médio");
  const [alts, setAlts] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [usarImagens, setUsarImagens] = useState(false);
  const [imagens, setImagens] = useState<File[]>([]);
  const [qtdImagens, setQtdImagens] = useState(0);

  const [enunciadosRaw, setEnunciadosRaw] = useState("");
  const enunciados = useMemo(() => splitEnunciados(enunciadosRaw), [enunciadosRaw]);

  async function addBloco(label: string, dificuldadeLabel: string, lista: ListaQuestoes, figurasPatch?: Record<string, string>) {
    const blocos = st.blocos || [];
    const bloco: BlocoQuestoes = { label, dificuldade: dificuldadeLabel, questoes: lista.questoes };
    const next = [...blocos, bloco];
    const figuras = { ...(st.figuras || {}), ...(figurasPatch || {}) };
    saveState({ blocos: next, figuras });
  }

  async function onGerar() {
    setError(null);
    setLoading(true);
    try {
      const questoes_exemplo = questoesExemplo.trim() ? questoesExemplo.trim() : null;
      if (usarImagens && qtdImagens > 0) {
        const imgs = imagens.slice(0, qtdImagens);
        const lista = await generateQuestionsWithImages({
          materia,
          assunto,
          dificuldade,
          num_alternativas: alts,
          questoes_exemplo,
          images: imgs
        });

        const figurasPatch: Record<string, string> = {};
        for (let i = 0; i < lista.questoes.length; i++) {
          const file = imgs[i];
          if (!file) continue;
          const key = crypto.randomUUID();
          figurasPatch[key] = await fileToDataUrl(file);
          (lista.questoes[i] as any).figura_key = key;
        }

        await addBloco(`⚡ Rápido (imagem) | ${materia} | ${assunto}`, `${dificuldade} • ${nivel}`, lista, figurasPatch);
      } else {
        const lista = await generateQuestions({
          materia,
          assunto,
          quantidade: qtd,
          dificuldade,
          nivel_ensino: nivel,
          num_alternativas: alts,
          incluir_texto_base: false,
          questoes_exemplo,
          analise_banca: null,
          analise_prova: null,
          edital: null
        });
        await addBloco(`⚡ Rápido | ${materia} | ${assunto}`, `${dificuldade} • ${nivel}`, lista);
      }
    } catch (err: any) {
      setError(err?.message || "Erro ao gerar");
    } finally {
      setLoading(false);
    }
  }

  async function onCompletar() {
    setError(null);
    setLoading(true);
    try {
      const questoes_exemplo = questoesExemplo.trim() ? questoesExemplo.trim() : null;
      const resultados = await Promise.all(
        enunciados.map((en) =>
          completeQuestion({
            enunciado: en,
            materia,
            assunto,
            num_alternativas: alts,
            questoes_exemplo,
            analise_banca: null,
            analise_prova: null
          })
        )
      );

      const questoes = resultados.map((r) => r.questoes[0]).filter(Boolean);
      const lista = { questoes } as ListaQuestoes;
      await addBloco(`✍️ Completadas | ${materia} | ${assunto}`, `${dificuldade} • ${nivel}`, lista);
    } catch (err: any) {
      setError(err?.message || "Erro ao completar");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h2>Questões rápidas</h2>
      <div className="muted">Geração sem edital/banca/prova (só matéria, assunto e parâmetros). Salva no seu navegador.</div>
      <div className="hr" />

      <div className="row">
        <div className="col">
          <label>Matéria</label>
          <input value={materia} onChange={(e) => setMateria(e.target.value)} />
        </div>
        <div className="col">
          <label>Assunto</label>
          <input value={assunto} onChange={(e) => setAssunto(e.target.value)} />
        </div>
        <div className="col">
          <label>Qtd.</label>
          <input type="number" value={qtd} onChange={(e) => setQtd(Number(e.target.value))} min={1} max={15} />
        </div>
      </div>

      <div style={{ height: 10 }} />

      <div className="row">
        <div className="col">
          <label>Modo</label>
          <select value={modo} onChange={(e) => setModo(e.target.value as any)}>
            <option value="gerar">Gerar do zero</option>
            <option value="completar">Completar questões coladas</option>
          </select>
        </div>
      </div>

      <div className="hr" />

      <label>Questões exemplo (opcional)</label>
      <div className="muted">
        Cole 1–2 questões reais (sem gabarito) para a IA imitar o “jeito” da banca (texto, pegadinhas, formato). O sistema não deve copiar o conteúdo,
        só o estilo.
      </div>
      <textarea value={questoesExemplo} onChange={(e) => setQuestoesExemplo(e.target.value)} />
      <div style={{ height: 10 }} />

      <div className="row">
        <div className="col">
          <label>Nível</label>
          <select value={nivel} onChange={(e) => setNivel(e.target.value as any)}>
            <option value="Fundamental">Fundamental</option>
            <option value="Médio">Médio</option>
            <option value="Superior">Superior</option>
          </select>
        </div>
        <div className="col">
          <label>Dificuldade</label>
          <select value={dificuldade} onChange={(e) => setDificuldade(e.target.value)}>
            <option value="Fácil">Fácil</option>
            <option value="Médio">Médio</option>
            <option value="Difícil">Difícil</option>
          </select>
        </div>
        <div className="col">
          <label>Alternativas</label>
          <select value={alts} onChange={(e) => setAlts(Number(e.target.value))}>
            <option value={4}>4 (A-D)</option>
            <option value={5}>5 (A-E)</option>
          </select>
        </div>
      </div>

      {modo === "gerar" ? (
        <>
          <div className="hr" />

          <div className="row">
            <div className="col">
              <label>
                <input type="checkbox" checked={usarImagens} onChange={(e) => setUsarImagens(e.target.checked)} /> Usar imagens
              </label>
              {usarImagens ? (
                <div style={{ marginTop: 10 }}>
                  <input
                    type="file"
                    accept="image/png,image/jpg,image/jpeg"
                    multiple
                    onChange={(e) => setImagens(Array.from(e.target.files || []))}
                  />
                  <div style={{ height: 10 }} />
                  <label>Qtd. de questões com imagem</label>
                  <input
                    type="number"
                    value={qtdImagens}
                    onChange={(e) => setQtdImagens(Number(e.target.value))}
                    min={0}
                    max={imagens.length}
                  />
                </div>
              ) : null}
            </div>
          </div>

          <div className="hr" />
          <button disabled={loading || !materia.trim() || !assunto.trim()} onClick={onGerar}>
            {loading ? "Gerando..." : "Gerar e adicionar no simulado"}
          </button>
        </>
      ) : (
        <>
          <h3>Completar questões coladas (mesmo conteúdo, padrão do simulado)</h3>
          <div className="muted">Cole várias questões e o sistema gera alternativas no mesmo padrão. Separe por linha em branco (ou numeração 1), 2), 3)...).</div>
          <textarea value={enunciadosRaw} onChange={(e) => setEnunciadosRaw(e.target.value)} />
          <div style={{ height: 10 }} />
          <button disabled={loading || enunciados.length === 0 || !materia.trim() || !assunto.trim()} onClick={onCompletar}>
            {loading ? "Gerando..." : "Gerar alternativas e adicionar no simulado"}
          </button>
        </>
      )}

      {error ? (
        <div className="muted" style={{ marginTop: 12, color: "#fca5a5" }}>
          {error}
        </div>
      ) : null}
    </div>
  );
}
