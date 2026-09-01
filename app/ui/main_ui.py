"""
Ponto de entrada principal da interface Streamlit.
Integra todos os agentes e telas do sistema.
"""
import sys
import os

# Garante que a raiz do projeto esteja no sys.path,
# independentemente de onde o Streamlit for chamado.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import streamlit as st
from uuid import uuid4
from app.config import settings
from app.agents.edital_agent import get_edital_agent
from app.agents.banca_agent import get_banca_agent
from app.agents.prova_agent import get_prova_agent
from app.agents.questoes_agent import gerar_questoes, gerar_questoes_com_imagens, completar_questao
from app.models.schemas import ListaQuestoes
from app.ui.components import render_questao, render_questao_prova
from app.services.file_service import extrair_texto_arquivo

# ──────────────────────────────────────────────────────
#  Configuração de página (deve ser a primeira chamada)
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="ConcursoAI – Seu Agente de Estudos",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────
#  CSS personalizado – tema dark premium
# ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Fundo geral */
.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    color: #e2e8f0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e1e3f 0%, #12122a 100%);
    border-right: 1px solid rgba(139, 92, 246, 0.2);
}
section[data-testid="stSidebar"] * {
    color: #c4b5fd !important;
}

/* Cabeçalho hero */
.hero-container {
    background: linear-gradient(135deg, rgba(139,92,246,0.15) 0%, rgba(59,130,246,0.15) 100%);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    text-align: center;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #94a3b8;
    margin-top: 0.5rem;
}

/* Cards de configuração */
.config-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.3s;
}
.config-card:hover {
    border-color: rgba(139,92,246,0.5);
}

/* Enunciado da questão */
.enunciado-box {
    background: rgba(255,255,255,0.04);
    border-left: 4px solid #8b5cf6;
    border-radius: 0 12px 12px 0;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    font-size: 0.98rem;
    line-height: 1.7;
    color: #e2e8f0;
}
.texto-base-box {
    background: rgba(255,255,255,0.03);
    border-left: 4px solid #60a5fa;
    border-radius: 0 12px 12px 0;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    font-size: 0.95rem;
    line-height: 1.7;
    color: #e2e8f0;
}

/* Resultado acerto */
.resultado-acerto {
    background: rgba(52,211,153,0.15);
    border: 1px solid rgba(52,211,153,0.4);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    color: #6ee7b7;
    font-size: 1.1rem;
    font-weight: 600;
    margin: 1rem 0;
    text-align: center;
}

/* Resultado erro */
.resultado-erro {
    background: rgba(239,68,68,0.12);
    border: 1px solid rgba(239,68,68,0.35);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    color: #fca5a5;
    font-size: 1rem;
    margin: 1rem 0;
    text-align: center;
}

/* Explicação */
.explicacao-box {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    color: #cbd5e1;
    line-height: 1.8;
    font-size: 0.92rem;
}

/* Stat cards de desempenho */
.stat-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
}
.stat-number {
    font-size: 3rem;
    font-weight: 700;
    line-height: 1;
}
.stat-label {
    font-size: 0.85rem;
    color: #94a3b8;
    margin-top: 0.4rem;
}

/* ─── Botões – todos os estados ─── */
.stButton > button,
.stButton > button:focus,
.stButton > button:active,
button[kind="primary"],
button[kind="secondary"],
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-minimal"] {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    padding: 0.55rem 1.4rem !important;
    box-shadow: 0 4px 15px rgba(124,58,237,0.3) !important;
}

.stButton > button:hover,
[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-secondary"]:hover {
    background: linear-gradient(135deg, #8b5cf6, #6366f1) !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(139,92,246,0.45) !important;
}

.stButton > button:disabled,
[data-testid="stBaseButton-primary"]:disabled,
[data-testid="stBaseButton-secondary"]:disabled {
    background: rgba(80,80,110,0.5) !important;
    color: rgba(255,255,255,0.4) !important;
    transform: none !important;
    box-shadow: none !important;
    cursor: not-allowed !important;
}

/* Garante que o texto dentro do botão seja sempre branco */
.stButton > button p,
.stButton > button span,
[data-testid="stBaseButton-primary"] p,
[data-testid="stBaseButton-secondary"] p {
    color: #ffffff !important;
    font-weight: 600 !important;
}


/* Abas */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #94a3b8;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: rgba(139,92,246,0.25) !important;
    color: #a78bfa !important;
}

/* ─── Inputs: fundo claro, texto PRETO – máxima legibilidade ─── */

/* Contêiner geral dos inputs */
.stTextInput > div > div,
.stTextArea > div > div,
.stNumberInput > div > div {
    background: #f8fafc !important;
    border: 2px solid #8b5cf6 !important;
    border-radius: 10px !important;
}

/* O elemento input/textarea em si */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
input[type="text"],
input[type="number"],
textarea {
    background: #f8fafc !important;
    color: #111827 !important;
    caret-color: #7c3aed !important;
    border: none !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
}

/* Placeholder cinza médio */
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #9ca3af !important;
    font-weight: 400 !important;
}

/* Borda roxa ao focar */
.stTextInput > div > div:focus-within,
.stTextArea > div > div:focus-within,
.stNumberInput > div > div:focus-within {
    border-color: #6d28d9 !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.25) !important;
}

/* Labels dos campos */
.stTextInput label, .stTextArea label,
.stSelectbox label, .stNumberInput label,
.stFileUploader label {
    color: #e2e8f0 !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}

/* SelectBox – fundo claro, texto preto */
.stSelectbox > div > div {
    background: #f8fafc !important;
    border: 2px solid #8b5cf6 !important;
    color: #111827 !important;
    border-radius: 10px !important;
}
.stSelectbox > div > div > div {
    color: #111827 !important;
}


/* Divider */
hr {
    border-color: rgba(139,92,246,0.15) !important;
}

/* Spinner */
.stSpinner > div {
    border-top-color: #8b5cf6 !important;
}

/* Badge de matéria na sidebar */
.materia-badge {
    background: rgba(139,92,246,0.2);
    border: 1px solid rgba(139,92,246,0.4);
    border-radius: 8px;
    padding: 0.3rem 0.8rem;
    font-size: 0.82rem;
    color: #c4b5fd;
    display: inline-block;
    margin: 2px;
}

/* Tag de status */
.status-ok {
    color: #34d399;
    font-weight: 600;
}
.status-pending {
    color: #fbbf24;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────
#  Inicializa o session_state
# ──────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "edital_obj": None,
        "analise_banca": None,
        "analise_prova": None,
        "blocos_questoes": [],   # lista de dicts {label, questoes}
        "figuras": {},
        "desempenho_acertos": 0,
        "desempenho_erros": 0,
        "total_questoes_respondidas": 0,
        "historico_desempenho": [],
        "config_concluida": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()


# ──────────────────────────────────────────────────────
#  Sidebar – Informações do projeto e status
# ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 ConcursoAI")
    st.markdown("*Seu agente de estudos personalizado*")
    st.divider()

    # Status dos módulos
    st.markdown("### Status da Sessão")

    edital_status = "✅ Edital analisado" if st.session_state.edital_obj else "⏳ Aguardando edital"
    banca_status  = "✅ Banca analisada"   if st.session_state.analise_banca else "⏳ Aguardando banca"
    prova_status  = "✅ Prova analisada"   if st.session_state.analise_prova else "➕ Prova opcional"

    st.markdown(f"- {edital_status}")
    st.markdown(f"- {banca_status}")
    st.markdown(f"- {prova_status}")

    st.divider()

    # Matérias disponíveis
    if st.session_state.edital_obj:
        st.markdown("### 📚 Matérias no Edital")
        for mat in st.session_state.edital_obj.materias:
            st.markdown(f'<span class="materia-badge">{mat.nome}</span>', unsafe_allow_html=True)

    st.divider()

    # Mini placar
    acertos = st.session_state.desempenho_acertos
    erros   = st.session_state.desempenho_erros
    total   = acertos + erros
    pct     = round((acertos / total * 100)) if total > 0 else 0

    st.markdown("### 🏆 Placar da Sessão")
    col_a, col_e = st.columns(2)
    col_a.metric("✅ Acertos", acertos)
    col_e.metric("❌ Erros", erros)
    if total > 0:
        st.progress(pct / 100, text=f"{pct}% de aproveitamento")

    st.divider()
    if st.button("🔄 Reiniciar Sessão", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ──────────────────────────────────────────────────────
#  Hero header
# ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🎓 ConcursoAI</div>
    <div class="hero-subtitle">
        Plataforma inteligente de estudos para concursos públicos<br>
        <small>Questões inéditas geradas por IA, no estilo da sua banca</small>
    </div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────
#  Abas principais
# ──────────────────────────────────────────────────────
tab_config, tab_rapido, tab_simulado, tab_desempenho = st.tabs([
    "⚙️  Configuração",
    "⚡  Questões Rápidas",
    "🎯  Simulado",
    "📊  Desempenho",
])


# ══════════════════════════════════════════════════════
#  ABA 1 – CONFIGURAÇÃO
# ══════════════════════════════════════════════════════
with tab_config:
    st.markdown("## ⚙️ Configure seu Estudo")
    st.markdown("Preencha as informações abaixo para personalizar as questões geradas.")
    st.divider()

    col_left, col_right = st.columns([1.2, 1], gap="large")

    with col_left:
        # ── Bloco: Banca
        st.markdown("### 🏛️ Banca Organizadora")
        st.caption("Selecione a banca ou escolha 'Outra' para digitar manualmente.")

        BANCAS = [
            "── Selecione uma banca ──",
            # Federais / Grandes bancas
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
            "COVEST-COPSET",
            "── Outra (digitar manualmente) ──",
        ]

        banca_selecionada = st.selectbox(
            "Banca organizadora",
            options=BANCAS,
            index=0,
            key="sel_banca_lista"
        )

        # Se selecionou "Outra" ou não selecionou nada válido, mostra campo manual
        eh_outra = banca_selecionada in [
            "── Selecione uma banca ──",
            "── Outra (digitar manualmente) ──",
        ]

        if eh_outra:
            nome_banca = st.text_input(
                "Digite o nome da banca",
                placeholder="Ex: COPS-UEL, Movens, Instituto Quadrix...",
                key="input_banca_manual"
            )
        else:
            nome_banca = banca_selecionada
            st.success(f"✅ Banca selecionada: **{nome_banca}**")


        # ── Bloco: Edital
        st.markdown("### 📋 Conteúdo Programático do Edital")
        st.caption("Faça upload do PDF do edital **ou** cole o conteúdo manualmente.")

        edital_upload = st.file_uploader(
            "📄 Upload do Edital (PDF ou TXT)",
            type=["pdf", "txt"],
            key="upload_edital",
            help="Faça upload do PDF para extrair automaticamente o conteúdo programático."
        )
        texto_edital_manual = st.text_area(
            "Ou cole o conteúdo programático manualmente",
            height=150,
            placeholder=(
                "Exemplo:\n"
                "Língua Portuguesa: Interpretação de textos; Pontuação; Concordância verbal.\n"
                "Matemática: Porcentagem; Regra de três; Raciocínio lógico.\n"
                "Direito Constitucional: Direitos fundamentais; Organização do Estado."
            ),
            key="input_edital"
        )
        # PDF tem prioridade sobre texto manual
        texto_edital = ""
        if edital_upload is not None:
            try:
                texto_edital = extrair_texto_arquivo(edital_upload)
                st.success(f"✅ PDF lido! {len(texto_edital):,} caracteres extraídos.")
            except Exception as e:
                st.error(f"Erro ao ler o PDF do edital: {e}")
        elif texto_edital_manual.strip():
            texto_edital = texto_edital_manual.strip()

    with col_right:
        # ── Bloco: Prova de referência
        st.markdown("### 📝 Prova de Referência *(opcional)*")
        st.caption("Faça upload do PDF da prova **ou** cole as questões manualmente.")

        prova_upload = st.file_uploader(
            "📄 Upload da Prova (PDF ou TXT)",
            type=["pdf", "txt"],
            key="upload_prova",
            help="Faça upload de uma prova anterior para o agente aprender o estilo da banca."
        )
        texto_prova_manual = st.text_area(
            "Ou cole as questões manualmente",
            height=150,
            placeholder=(
                "Cole aqui questões de provas anteriores da banca.\n"
                "Isso melhora a qualidade das questões geradas.\n\n"
                "Exemplo:\n"
                "1. Questão sobre interpretação de texto...\n"
                "A) alternativa  B) alternativa..."
            ),
            key="input_prova"
        )
        # PDF tem prioridade sobre texto manual
        texto_prova = ""
        if prova_upload is not None:
            try:
                texto_prova = extrair_texto_arquivo(prova_upload)
                st.success(f"✅ PDF da prova lido! {len(texto_prova):,} caracteres extraídos.")
            except Exception as e:
                st.error(f"Erro ao ler o PDF da prova: {e}")
        elif texto_prova_manual.strip():
            texto_prova = texto_prova_manual.strip()

        st.markdown("### ℹ️ Como funciona")
        st.info(
            "1. **Análise do Edital** → O agente lê e estrutura o conteúdo programático.\n\n"
            "2. **Perfil da Banca** → O sistema carrega o histórico e as características da banca informada.\n\n"
            "3. **Prova de referência** → Analisa o estilo da prova para gerar questões mais fiéis.\n\n"
            "4. **Geração** → Tudo é combinado para criar questões inéditas e precisas."
        )

    st.divider()

    # ── Botão de análise
    btn_analisar = st.button(
        "🚀 Analisar e Preparar Estudo",
        use_container_width=True,
        disabled=not (nome_banca.strip() and texto_edital.strip()),
        key="btn_analisar"
    )

    if not (nome_banca.strip() and texto_edital.strip()):
        st.caption("⚠️ Preencha ao menos o nome da banca e o conteúdo programático para continuar.")

    if btn_analisar:
        progress_bar = st.progress(0, text="Iniciando análise...")

        with st.spinner(""):
            # Passo 1: Analisar edital
            progress_bar.progress(10, text="📋 Analisando conteúdo programático do edital...")
            try:
                edital_agent = get_edital_agent()
                resp_edital = edital_agent.run(texto_edital)
                st.session_state.edital_obj = resp_edital.content
            except Exception as e:
                st.error(f"Erro ao analisar o edital: {e}")
                st.stop()

            # Passo 2: Analisar banca
            progress_bar.progress(45, text="🏛️ Carregando perfil da banca organizadora...")
            try:
                banca_agent = get_banca_agent()
                resp_banca = banca_agent.run(nome_banca)
                st.session_state.analise_banca = resp_banca.content
            except Exception as e:
                st.warning(f"Não foi possível analisar a banca: {e}. Continuando sem esse contexto.")

            # Passo 3: Analisar prova (opcional)
            if texto_prova.strip():
                progress_bar.progress(70, text="📝 Analisando estilo da prova de referência...")
                try:
                    prova_agent = get_prova_agent()
                    resp_prova = prova_agent.run(texto_prova)
                    st.session_state.analise_prova = resp_prova.content
                except Exception as e:
                    st.warning(f"Não foi possível analisar a prova: {e}")

            progress_bar.progress(100, text="✅ Análise concluída!")
            st.session_state.config_concluida = True

        st.success("✅ Tudo pronto! Vá para a aba **🎯 Simulado** para gerar suas questões.")

        # Mostra resumo das matérias
        if st.session_state.edital_obj:
            st.markdown("#### 📚 Matérias identificadas no edital:")
            cols = st.columns(3)
            for i, mat in enumerate(st.session_state.edital_obj.materias):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="config-card">
                        <strong>{mat.nome}</strong><br>
                        <small style="color:#94a3b8">{len(mat.assuntos)} assunto(s) identificado(s)</small>
                    </div>
                    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  ABA 2 – QUESTÕES RÁPIDAS
# ══════════════════════════════════════════════════════
with tab_rapido:
    st.markdown("## ⚡ Questões Rápidas")
    st.caption("Gere questões sem analisar banca, edital ou prova. Informe apenas matéria, assunto e parâmetros.")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        materia_rapida = st.text_input("📚 Matéria", placeholder="Ex: Engenharia Elétrica", key="rapido_materia")
    with col_b:
        assunto_rapido = st.text_input("📂 Assunto", placeholder="Ex: Circuitos trifásicos (Y/Δ)", key="rapido_assunto")
    with col_c:
        qtd_rapida = st.number_input("🔢 Qtd. de questões", min_value=1, max_value=15, value=5, step=1, key="rapido_qtd")

    col_d, col_e, col_f = st.columns(3)
    with col_d:
        nivel_ensino = st.selectbox(
            "🎓 Nível de ensino",
            options=["Fundamental", "Médio", "Superior"],
            index=2,
            key="rapido_nivel"
        )
    with col_e:
        dificuldade_rapida = st.selectbox(
            "⚡ Dificuldade",
            options=["Fácil", "Médio", "Difícil"],
            index=1,
            key="rapido_dificuldade"
        )
    with col_f:
        num_alts_rapida = st.selectbox(
            "🔤 Alternativas",
            options=[4, 5],
            index=1,
            format_func=lambda x: f"{x} alternativas (A-{'D' if x==4 else 'E'})",
            key="rapido_alternativas"
        )

    btn_rapido = st.button("⚡ Gerar questões rápidas", width="stretch", key="btn_rapido")

    if btn_rapido:
        if not materia_rapida.strip() or not assunto_rapido.strip():
            st.warning("⚠️ Preencha matéria e assunto para gerar as questões.")
            st.stop()

        keys_to_del = [k for k in st.session_state if k.startswith("q_") or k.startswith("radio_")]
        for k in keys_to_del:
            del st.session_state[k]

        with st.spinner("🤖 Gerando questões rápidas..."):
            try:
                lista = gerar_questoes(
                    materia=materia_rapida.strip(),
                    assunto=assunto_rapido.strip(),
                    quantidade=int(qtd_rapida),
                    dificuldade=dificuldade_rapida,
                    nivel_ensino=nivel_ensino,
                    num_alternativas=num_alts_rapida,
                    analise_banca=None,
                    analise_prova=None,
                    edital=None,
                )
            except Exception as e:
                st.error(f"❌ Erro ao gerar: {e}")
                st.stop()

        st.success(f"✅ {len(lista.questoes)} questão(ões) gerada(s)!")

        bloco = {
            "label": f"⚡ Rápido | {materia_rapida.strip()} | {assunto_rapido.strip()}",
            "dificuldade": f"{dificuldade_rapida} • {nivel_ensino}",
            "questoes": lista.questoes,
        }
        st.session_state.blocos_questoes.append(bloco)

        st.info("As questões foram adicionadas ao seu Simulado. Vá para a aba 🎯 Simulado para responder e acompanhar no 📊 Desempenho.")

    st.divider()
    st.markdown("### ✍️ Completar enunciados (gerar alternativas)")
    st.caption("Cole várias questões sem alternativas. O sistema cria as alternativas, você responde e só depois corrige.")

    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        materia_completar = st.text_input("📚 Matéria (para completar)", value=materia_rapida, key="comp_materia")
    with col_c2:
        assunto_completar = st.text_input("📂 Assunto (para completar)", value=assunto_rapido, key="comp_assunto")
    with col_c3:
        num_alts_comp = st.selectbox(
            "🔤 Alternativas (completar)",
            options=[4, 5],
            index=1,
            format_func=lambda x: f"{x} alternativas (A-{'D' if x==4 else 'E'})",
            key="comp_alternativas"
        )

    texto_enunciados = st.text_area(
        "Cole os enunciados (1 por bloco, separado por linha em branco):",
        height=220,
        placeholder="Ex:\n1) Em um diagrama unifilar...\n\n2) No circuito trifásico em Y...\n\n3) Em um comando de motor...\n",
        key="comp_enunciados"
    )

    col_btnc1, col_btnc2 = st.columns(2)
    with col_btnc1:
        btn_gerar_alt = st.button("Gerar alternativas", width="stretch", key="btn_comp_gerar")
    with col_btnc2:
        btn_limpar_comp = st.button("Limpar", width="stretch", key="btn_comp_limpar")

    if btn_limpar_comp:
        st.session_state["comp_questoes"] = []
        st.session_state["comp_corrigir"] = False
        keys_to_del = [k for k in st.session_state if k.startswith("pcomp_") or k.startswith("radio_pcomp_")]
        for k in keys_to_del:
            del st.session_state[k]
        st.rerun()

    if btn_gerar_alt:
        if not materia_completar.strip() or not assunto_completar.strip():
            st.warning("⚠️ Preencha matéria e assunto.")
            st.stop()
        if not texto_enunciados.strip():
            st.warning("⚠️ Cole pelo menos um enunciado.")
            st.stop()

        bruto = texto_enunciados.replace("\r\n", "\n").strip()
        blocos = [b.strip() for b in bruto.split("\n\n") if b.strip()]
        if not blocos:
            st.warning("⚠️ Não consegui separar os enunciados. Separe cada questão por uma linha em branco.")
            st.stop()

        keys_to_del = [k for k in st.session_state if k.startswith("pcomp_") or k.startswith("radio_pcomp_")]
        for k in keys_to_del:
            del st.session_state[k]

        st.session_state["comp_corrigir"] = False
        questoes_comp = []
        progresso = st.progress(0, text="Gerando alternativas...")
        total = len(blocos)
        for i, en in enumerate(blocos, start=1):
            resp = completar_questao(
                enunciado=en,
                materia=materia_completar.strip(),
                assunto=assunto_completar.strip(),
                num_alternativas=num_alts_comp,
                analise_banca=None,
                analise_prova=None,
            )
            q = resp.questoes[0]
            q.numero = i
            questoes_comp.append(q)
            progresso.progress(int(i / total * 100), text=f"Gerando alternativas... ({i}/{total})")

        st.session_state["comp_questoes"] = questoes_comp
        st.success(f"✅ Alternativas geradas para {len(questoes_comp)} questão(ões)!")

    questoes_comp = st.session_state.get("comp_questoes", [])
    if questoes_comp:
        correcao = st.session_state.get("comp_corrigir", False)
        st.divider()
        st.markdown("### 📝 Responder (modo prova)")

        for idx, q in enumerate(questoes_comp):
            render_questao_prova(q, index=idx, session_prefix="pcomp", correcao_liberada=correcao)

        if not correcao:
            if st.button("Finalizar e corrigir", width="stretch", type="primary", key="btn_comp_corrigir"):
                st.session_state["comp_corrigir"] = True
                st.rerun()


# ══════════════════════════════════════════════════════
#  ABA 3 – SIMULADO
# ══════════════════════════════════════════════════════
with tab_simulado:
    st.markdown("## 🎯 Gerar Simulado")

    if not st.session_state.config_concluida:
        st.warning("⚠️ Configure o edital e a banca na aba **⚙️ Configuração** antes de gerar questões.")
        st.stop()

    # ── Painel de controle das questões
    with st.container():
        st.markdown("### 🎛️ Parâmetros do Simulado")
        
        modo_geracao = st.radio(
            "Modo de Geração",
            options=["✨ Gerar Questões Inéditas", "✍️ Completar Questão Existente"],
            horizontal=True,
            help="Escolha se deseja que a IA invente questões do zero ou gere alternativas para um enunciado que você já tem."
        )
        
        col1, col2, col3 = st.columns(3)

        # Selecionar matéria
        with col1:
            materias_disponiveis = [m.nome for m in st.session_state.edital_obj.materias] if st.session_state.edital_obj else []
            materia_selecionada = st.selectbox(
                "📚 Matéria",
                options=materias_disponiveis,
                key="sel_materia"
            )

        # Selecionar assunto com base na matéria
        with col2:
            assuntos_disponiveis = []
            assunto_obj_atual = None
            if materia_selecionada and st.session_state.edital_obj:
                for mat in st.session_state.edital_obj.materias:
                    if mat.nome == materia_selecionada:
                        assuntos_disponiveis = [a.nome for a in mat.assuntos]
                        break
                if not assuntos_disponiveis:
                    assuntos_disponiveis = ["Geral"]

            assunto_selecionado = st.selectbox(
                "📂 Assunto",
                options=assuntos_disponiveis,
                key="sel_assunto"
            )

        # Selecionar tópico com base no assunto
        with col3:
            topicos_disponiveis = ["Todos os tópicos"]
            if materia_selecionada and assunto_selecionado and st.session_state.edital_obj:
                for mat in st.session_state.edital_obj.materias:
                    if mat.nome == materia_selecionada:
                        for ass in mat.assuntos:
                            if ass.nome == assunto_selecionado:
                                if ass.topicos:
                                    topicos_disponiveis += [t.nome for t in ass.topicos]
                                break
                        break

            topico_selecionado = st.selectbox(
                "📄 Tópico específico",
                options=topicos_disponiveis,
                key="sel_topico",
                help="Filtre por um tópico específico do edital para questões ainda mais precisas."
            )

        # Segunda linha de controles
        col4, col5, col6 = st.columns(3)
        with col4:
            if modo_geracao == "✨ Gerar Questões Inéditas":
                dificuldade = st.selectbox(
                    "⚡ Dificuldade",
                    options=["Fácil", "Médio", "Difícil", "Avançado", "Estilo da Banca"],
                    index=1,
                    key="sel_dificuldade"
                )
            else:
                dificuldade = "Estilo da Banca"
                st.info("A dificuldade das alternativas se ajustará ao seu enunciado.")

        with col5:
            if modo_geracao == "✨ Gerar Questões Inéditas":
                quantidade = st.number_input(
                    "🔢 Qtd. de Questões",
                    min_value=1, max_value=10, value=3, step=1,
                    key="num_questoes"
                )
            else:
                quantidade = 1

        with col6:
            num_alternativas = st.selectbox(
                "🔤 Alternativas",
                options=[4, 5],
                index=1,
                format_func=lambda x: f"{x} alternativas (A-{'D' if x==4 else 'E'})",
                key="sel_alternativas"
            )

        usar_texto_base = False
        qtd_texto_base = 0
        modo_texto_base = None
        texto_base_fornecido = ""
        usar_imagens = False
        imagens_upload = []
        qtd_imagens = 0

        if modo_geracao == "✨ Gerar Questões Inéditas":
            with st.expander("⚙️ Opções flexíveis (texto base / diagramas)", expanded=False):
                col_opt1, col_opt2 = st.columns(2)

                with col_opt1:
                    usar_texto_base = st.checkbox(
                        "Incluir texto-base para interpretação/análise",
                        value=False,
                        key="opt_texto_base"
                    )
                    if usar_texto_base:
                        qtd_texto_base = st.number_input(
                            "Qtd. de questões com texto-base",
                            min_value=0,
                            max_value=int(quantidade),
                            value=min(1, int(quantidade)),
                            step=1,
                            key="qtd_texto_base"
                        )
                        modo_texto_base = st.radio(
                            "Texto-base",
                            options=["IA gera", "Eu forneço"],
                            horizontal=True,
                            key="modo_texto_base"
                        )
                        if modo_texto_base == "Eu forneço":
                            texto_base_fornecido = st.text_area(
                                "Cole o texto-base (será usado nas questões com texto-base)",
                                height=150,
                                key="texto_base_fornecido"
                            )

                with col_opt2:
                    usar_imagens = st.checkbox(
                        "Gerar questões a partir de imagens (diagramas/figuras)",
                        value=False,
                        key="opt_imagens"
                    )
                    if usar_imagens:
                        imagens_upload = st.file_uploader(
                            "Upload de imagens (PNG/JPG/JPEG)",
                            type=["png", "jpg", "jpeg"],
                            accept_multiple_files=True,
                            key="upload_imagens_simulado"
                        ) or []
                        qtd_imagens = st.number_input(
                            "Qtd. de questões com imagem",
                            min_value=0,
                            max_value=int(quantidade),
                            value=min(len(imagens_upload), int(quantidade)),
                            step=1,
                            key="qtd_imagens"
                        )

        if modo_geracao == "✍️ Completar Questão Existente":
            texto_enunciado = st.text_area(
                "Cole o enunciado da questão aqui:",
                height=150,
                placeholder="Ex: Em uma instalação elétrica residencial bifásica (220V/127V), deseja-se instalar um chuveiro de 5500W...",
                key="input_enunciado_completar"
            )

    st.divider()

    # Monta o label do botão conforme o modo e tópico
    if modo_geracao == "✍️ Completar Questão Existente":
        label_btn = f"✍️ Gerar {num_alternativas} alternativas para o enunciado colado"
        assunto_para_gerar = f"{assunto_selecionado}"
    else:
        if topico_selecionado and topico_selecionado != "Todos os tópicos":
            label_btn = f"✨ Gerar {quantidade} Questão(ões) — {topico_selecionado}"
            assunto_para_gerar = f"{assunto_selecionado} – Tópico: {topico_selecionado}"
        else:
            label_btn = f"✨ Gerar {quantidade} Questão(ões) — {assunto_selecionado or 'Geral'}"
            assunto_para_gerar = assunto_selecionado or "Geral"

    btn_gerar = st.button(
        label_btn,
        use_container_width=True,
        key="btn_gerar"
    )

    if btn_gerar:
        if modo_geracao == "✍️ Completar Questão Existente" and not texto_enunciado.strip():
            st.warning("⚠️ Cole o enunciado da questão primeiro!")
            st.stop()

        if modo_geracao == "✨ Gerar Questões Inéditas":
            if usar_texto_base and qtd_texto_base > 0 and modo_texto_base == "Eu forneço" and not texto_base_fornecido.strip():
                st.warning("⚠️ Cole o texto-base ou reduza a quantidade de questões com texto-base.")
                st.stop()

            if usar_imagens and qtd_imagens > 0 and len(imagens_upload) < int(qtd_imagens):
                st.warning("⚠️ Envie imagens suficientes ou reduza a quantidade de questões com imagem.")
                st.stop()

            if int(qtd_texto_base) + int(qtd_imagens) > int(quantidade):
                st.warning("⚠️ A soma de questões com texto-base e com imagem não pode ser maior que a quantidade total.")
                st.stop()
            
        st.session_state.questoes_geradas = None  # Limpa questões anteriores
        # Limpa estados de respostas anteriores
        keys_to_del = [k for k in st.session_state if k.startswith("q_") or k.startswith("radio_")]
        for k in keys_to_del:
            del st.session_state[k]

        with st.spinner(f"🤖 Gerando {'alternativas' if modo_geracao == '✍️ Completar Questão Existente' else 'questões inéditas'}... Aguarde."):
            try:
                if modo_geracao == "✨ Gerar Questões Inéditas":
                    total_qtd = int(quantidade)
                    qtd_imagens_eff = int(qtd_imagens) if usar_imagens else 0
                    qtd_texto_eff = int(qtd_texto_base) if usar_texto_base else 0
                    qtd_normal = total_qtd - qtd_imagens_eff - qtd_texto_eff

                    questoes_total = []

                    if qtd_imagens_eff > 0:
                        imagens_bytes = []
                        figura_keys = []
                        for up in imagens_upload[:qtd_imagens_eff]:
                            figura_key = str(uuid4())
                            figura_keys.append(figura_key)
                            img_bytes = up.getvalue()
                            st.session_state.figuras[figura_key] = img_bytes
                            imagens_bytes.append((img_bytes, up.type or "image/png"))

                        lista_img = gerar_questoes_com_imagens(
                            materia=materia_selecionada,
                            assunto=assunto_para_gerar,
                            imagens=imagens_bytes,
                            dificuldade=dificuldade,
                            num_alternativas=num_alternativas,
                            analise_banca=st.session_state.analise_banca,
                            analise_prova=st.session_state.analise_prova,
                            edital=st.session_state.edital_obj,
                        )
                        for q, fk in zip(lista_img.questoes, figura_keys):
                            q.figura_key = fk
                        questoes_total.extend(lista_img.questoes)

                    if qtd_texto_eff > 0:
                        lista_tb = gerar_questoes(
                            materia=materia_selecionada,
                            assunto=assunto_para_gerar,
                            quantidade=qtd_texto_eff,
                            dificuldade=dificuldade,
                            num_alternativas=num_alternativas,
                            incluir_texto_base=True,
                            modo_texto_base="fornecido" if modo_texto_base == "Eu forneço" else "gerar",
                            texto_base_fornecido=texto_base_fornecido.strip() if modo_texto_base == "Eu forneço" else None,
                            analise_banca=st.session_state.analise_banca,
                            analise_prova=st.session_state.analise_prova,
                            edital=st.session_state.edital_obj,
                        )
                        questoes_total.extend(lista_tb.questoes)

                    if qtd_normal > 0:
                        lista_normal = gerar_questoes(
                            materia=materia_selecionada,
                            assunto=assunto_para_gerar,
                            quantidade=qtd_normal,
                            dificuldade=dificuldade,
                            num_alternativas=num_alternativas,
                            analise_banca=st.session_state.analise_banca,
                            analise_prova=st.session_state.analise_prova,
                            edital=st.session_state.edital_obj,
                        )
                        questoes_total.extend(lista_normal.questoes)

                    lista = ListaQuestoes(questoes=questoes_total)
                    bloco_label = f"{materia_selecionada} | {assunto_selecionado}" + (f" → {topico_selecionado}" if topico_selecionado != "Todos os tópicos" else "")
                else:
                    lista = completar_questao(
                        enunciado=texto_enunciado.strip(),
                        materia=materia_selecionada,
                        assunto=assunto_selecionado,
                        num_alternativas=num_alternativas,
                        analise_banca=st.session_state.analise_banca,
                        analise_prova=st.session_state.analise_prova,
                    )
                    bloco_label = f"✨ Completada | {materia_selecionada} | {assunto_selecionado}"

                # Calcula o índice de partida para numeração contínua
                total_anterior = sum(len(b["questoes"]) for b in st.session_state.blocos_questoes)
                # Renumera as questões para continuar a partir do bloco anterior
                for i, q in enumerate(lista.questoes):
                    q.numero = total_anterior + i + 1

                bloco = {
                    "label": bloco_label,
                    "dificuldade": dificuldade,
                    "questoes": lista.questoes,
                }
                st.session_state.blocos_questoes.append(bloco)
            except Exception as e:
                st.error(f"❌ Erro ao gerar: {e}")
                st.stop()

        st.success(f"✅ {len(lista.questoes)} questão(ões) gerada(s) com sucesso!")

    # ── Exibe todos os blocos acumulados
    if st.session_state.blocos_questoes:
        st.divider()

        total_simulado = sum(len(b["questoes"]) for b in st.session_state.blocos_questoes)
        col_info, col_limpar = st.columns([3, 1])
        with col_info:
            st.markdown(f"### 📝 Simulado — {total_simulado} questão(oes) no total")
        with col_limpar:
            if st.button("🗑️ Limpar tudo", key="btn_limpar", use_container_width=True):
                st.session_state.blocos_questoes = []
                st.session_state.figuras = {}
                keys_to_del = [k for k in st.session_state if k.startswith("q_") or k.startswith("radio_")]
                for k in keys_to_del:
                    del st.session_state[k]
                st.rerun()

        idx_global = 0
        for bloco_idx, bloco in enumerate(st.session_state.blocos_questoes):
            st.markdown(f"""
            <div style='background:rgba(139,92,246,0.12); border-left:4px solid #8b5cf6;
                        border-radius:0 10px 10px 0; padding:0.7rem 1.2rem; margin:1.5rem 0 0.8rem 0;'>
                <strong style='color:#c4b5fd'>📚 {bloco['label']}</strong>
                <span style='color:#94a3b8; font-size:0.85rem; margin-left:0.8rem'>
                    {len(bloco['questoes'])} questão(oes) • {bloco['dificuldade']}
                </span>
            </div>
            """, unsafe_allow_html=True)

            for questao in bloco["questoes"]:
                render_questao(questao, index=idx_global, session_prefix="q")
                idx_global += 1


# ══════════════════════════════════════════════════════
#  ABA 3 – DESEMPENHO
# ══════════════════════════════════════════════════════
with tab_desempenho:
    st.markdown("## 📊 Seu Desempenho")

    acertos = st.session_state.desempenho_acertos
    erros   = st.session_state.desempenho_erros
    total   = acertos + erros
    pct     = round((acertos / total * 100)) if total > 0 else 0

    if total == 0:
        st.info("💡 Responda questões na aba **🎯 Simulado** para acompanhar seu desempenho aqui!")
    else:
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number" style="color:#60a5fa">{total}</div>
                <div class="stat-label">Total Respondidas</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number" style="color:#34d399">{acertos}</div>
                <div class="stat-label">✅ Acertos</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number" style="color:#f87171">{erros}</div>
                <div class="stat-label">❌ Erros</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            cor_pct = "#34d399" if pct >= 60 else "#fbbf24" if pct >= 40 else "#f87171"
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number" style="color:{cor_pct}">{pct}%</div>
                <div class="stat-label">Aproveitamento</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Barra de progresso visual
        st.markdown("#### Aproveitamento geral")
        st.progress(pct / 100)

        if pct >= 70:
            st.success("🏆 Excelente! Você está indo muito bem. Continue assim!")
        elif pct >= 50:
            st.warning("📈 Bom progresso! Revise os temas em que errou para melhorar ainda mais.")
        else:
            st.error("📚 Continue estudando! Revise os conteúdos e pratique mais questões.")

        st.divider()
        st.info(
            "📌 **Próximas funcionalidades** (em desenvolvimento):\n"
            "- Histórico de desempenho por matéria e assunto\n"
            "- Gráficos de evolução ao longo do tempo\n"
            "- Ranking de assuntos com maior taxa de erro\n"
            "- Exportação do relatório de desempenho em PDF"
        )
