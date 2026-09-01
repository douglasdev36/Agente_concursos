"""
Componentes reutilizáveis da interface Streamlit.
Contém funções para renderizar questões, alternativas e cards de desempenho.
"""
import streamlit as st
from app.models.schemas import Questao, ListaQuestoes


def render_questao(questao: Questao, index: int, session_prefix: str = "q"):
    """
    Renderiza uma questão completa com alternativas, botão de resposta e gabarito.

    Args:
        questao: O objeto Questao do Pydantic
        index: Índice da questão na lista (para chaves únicas no session_state)
        session_prefix: Prefixo para evitar colisões de chaves
    """
    key_resposta = f"{session_prefix}_{index}_resposta"
    key_revealed = f"{session_prefix}_{index}_revealed"
    key_selected = f"{session_prefix}_{index}_selected"

    # Inicializa o estado da questão se não existir
    if key_resposta not in st.session_state:
        st.session_state[key_resposta] = None
    if key_revealed not in st.session_state:
        st.session_state[key_revealed] = False
    if key_selected not in st.session_state:
        st.session_state[key_selected] = None

    # Header da questão
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"### Questão {questao.numero}")
    with col2:
        nivel_color = {
            "Fácil": "🟢", "Medio": "🟡", "Médio": "🟡",
            "Dificil": "🔴", "Difícil": "🔴", "Avancado": "🟣", "Avançado": "🟣"
        }
        emoji = nivel_color.get(questao.dificuldade, "⚪")
        st.markdown(f"**{emoji} {questao.dificuldade}**")
    with col3:
        st.caption(f"📚 {questao.materia}")

    texto_base = getattr(questao, "texto_base", None)
    titulo_texto_base = getattr(questao, "titulo_texto_base", None)
    if texto_base:
        header_texto = f"<strong>{titulo_texto_base}</strong><br>" if titulo_texto_base else ""
        st.markdown(f"""
        <div class="texto-base-box">
            {header_texto}{texto_base}
        </div>
        """, unsafe_allow_html=True)

    figura_key = getattr(questao, "figura_key", None)
    figuras = st.session_state.get("figuras", {})
    figura = figuras.get(figura_key) if figura_key else None
    if figura:
        st.image(figura, use_container_width=True)

    # Enunciado
    st.markdown(f"""
    <div class="enunciado-box">
        {questao.enunciado}
    </div>
    """, unsafe_allow_html=True)

    # Alternativas como radio buttons
    opcoes = {alt.letra: f"**{alt.letra})** {alt.texto}" for alt in questao.alternativas}
    letras = list(opcoes.keys())

    if not st.session_state[key_revealed]:
        # Seleção de resposta
        escolha = st.radio(
            "Selecione sua resposta:",
            options=letras,
            format_func=lambda x: opcoes[x],
            key=f"radio_{session_prefix}_{index}",
            index=None
        )
        if escolha:
            st.session_state[key_selected] = escolha

        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            if st.button(
                "✅ Ver Resposta",
                key=f"btn_reveal_{session_prefix}_{index}",
                disabled=st.session_state[key_selected] is None,
                use_container_width=True
            ):
                st.session_state[key_revealed] = True
                st.session_state[key_resposta] = st.session_state[key_selected]
                st.rerun()
    else:
        # Mostra resultado
        resposta_usuario = st.session_state[key_resposta]
        gabarito = questao.resposta_correta.upper()
        acertou = resposta_usuario == gabarito

        # Exibe alternativas coloridas
        for alt in questao.alternativas:
            letra = alt.letra.upper()
            if letra == gabarito and letra == resposta_usuario:
                st.success(f"✅ **{letra})** {alt.texto} ← Sua resposta (CORRETA!)")
            elif letra == gabarito:
                st.success(f"✅ **{letra})** {alt.texto} ← Gabarito")
            elif letra == resposta_usuario:
                st.error(f"❌ **{letra})** {alt.texto} ← Sua resposta (INCORRETA)")
            else:
                st.markdown(f"&nbsp;&nbsp;&nbsp;{letra}) {alt.texto}")

        # Resultado
        if acertou:
            st.balloons()
            st.markdown("""
            <div class="resultado-acerto">
                🎉 Parabéns! Você acertou esta questão!
            </div>
            """, unsafe_allow_html=True)
            # Registra acerto no desempenho
            if f"{session_prefix}_{index}_contabilizado" not in st.session_state:
                st.session_state["desempenho_acertos"] = st.session_state.get("desempenho_acertos", 0) + 1
                st.session_state[f"{session_prefix}_{index}_contabilizado"] = True
        else:
            st.markdown(f"""
            <div class="resultado-erro">
                ❌ Resposta incorreta. O gabarito é: <strong>{gabarito}</strong>
            </div>
            """, unsafe_allow_html=True)
            if f"{session_prefix}_{index}_contabilizado" not in st.session_state:
                st.session_state["desempenho_erros"] = st.session_state.get("desempenho_erros", 0) + 1
                st.session_state[f"{session_prefix}_{index}_contabilizado"] = True

        # Explicação — sempre expandida quando errou
        with st.expander("📖 Ver Explicação e Referências", expanded=not acertou):
            # Explicação detalhada
            st.markdown(f"""
            <div class="explicacao-box">
                {questao.explicacao}
            </div>
            """, unsafe_allow_html=True)

            # Referências de estudo
            refs = getattr(questao, "referencias", [])
            if refs:
                st.markdown("#### 📌 Onde estudar este conteúdo:")
                refs_html = "".join([
                    f'<span style="display:inline-block; background:rgba(139,92,246,0.18); '
                    f'border:1px solid rgba(139,92,246,0.45); border-radius:8px; '
                    f'padding:0.25rem 0.75rem; margin:3px; font-size:0.85rem; color:#c4b5fd;">'
                    f'📎 {ref}</span>'
                    for ref in refs
                ])
                st.markdown(f'<div style="margin-top:0.5rem">{refs_html}</div>',
                            unsafe_allow_html=True)

            st.caption(f"📚 {questao.materia} → {questao.assunto}")

    st.divider()


def render_questao_prova(questao: Questao, index: int, session_prefix: str = "p", correcao_liberada: bool = False):
    key_resposta = f"{session_prefix}_{index}_resposta"
    key_selected = f"{session_prefix}_{index}_selected"

    if key_resposta not in st.session_state:
        st.session_state[key_resposta] = None
    if key_selected not in st.session_state:
        st.session_state[key_selected] = None

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"### Questão {questao.numero}")
    with col2:
        nivel_color = {
            "Fácil": "🟢", "Medio": "🟡", "Médio": "🟡",
            "Dificil": "🔴", "Difícil": "🔴", "Avancado": "🟣", "Avançado": "🟣"
        }
        emoji = nivel_color.get(questao.dificuldade, "⚪")
        st.markdown(f"**{emoji} {questao.dificuldade}**")
    with col3:
        st.caption(f"📚 {questao.materia}")

    texto_base = getattr(questao, "texto_base", None)
    titulo_texto_base = getattr(questao, "titulo_texto_base", None)
    if texto_base:
        header_texto = f"<strong>{titulo_texto_base}</strong><br>" if titulo_texto_base else ""
        st.markdown(f"""
        <div class="texto-base-box">
            {header_texto}{texto_base}
        </div>
        """, unsafe_allow_html=True)

    figura_key = getattr(questao, "figura_key", None)
    figuras = st.session_state.get("figuras", {})
    figura = figuras.get(figura_key) if figura_key else None
    if figura:
        st.image(figura, use_container_width=True)

    st.markdown(f"""
    <div class="enunciado-box">
        {questao.enunciado}
    </div>
    """, unsafe_allow_html=True)

    opcoes = {alt.letra: f"**{alt.letra})** {alt.texto}" for alt in questao.alternativas}
    letras = list(opcoes.keys())

    if not correcao_liberada:
        escolha = st.radio(
            "Selecione sua resposta:",
            options=letras,
            format_func=lambda x: opcoes[x],
            key=f"radio_{session_prefix}_{index}",
            index=None
        )
        if escolha:
            st.session_state[key_selected] = escolha
            st.session_state[key_resposta] = escolha
    else:
        resposta_usuario = st.session_state.get(key_resposta)
        gabarito = questao.resposta_correta.upper()
        acertou = resposta_usuario == gabarito

        for alt in questao.alternativas:
            letra = alt.letra.upper()
            if letra == gabarito and letra == resposta_usuario:
                st.success(f"✅ **{letra})** {alt.texto} ← Sua resposta (CORRETA!)")
            elif letra == gabarito:
                st.success(f"✅ **{letra})** {alt.texto} ← Gabarito")
            elif letra == resposta_usuario:
                st.error(f"❌ **{letra})** {alt.texto} ← Sua resposta (INCORRETA)")
            else:
                st.markdown(f"&nbsp;&nbsp;&nbsp;{letra}) {alt.texto}")

        if resposta_usuario is None:
            st.warning(f"⚠️ Sem resposta marcada. Gabarito: {gabarito}")
        elif acertou:
            st.markdown("""
            <div class="resultado-acerto">
                🎉 Parabéns! Você acertou esta questão!
            </div>
            """, unsafe_allow_html=True)
            if f"{session_prefix}_{index}_contabilizado" not in st.session_state:
                st.session_state["desempenho_acertos"] = st.session_state.get("desempenho_acertos", 0) + 1
                st.session_state[f"{session_prefix}_{index}_contabilizado"] = True
        else:
            st.markdown(f"""
            <div class="resultado-erro">
                ❌ Resposta incorreta. O gabarito é: <strong>{gabarito}</strong>
            </div>
            """, unsafe_allow_html=True)
            if f"{session_prefix}_{index}_contabilizado" not in st.session_state:
                st.session_state["desempenho_erros"] = st.session_state.get("desempenho_erros", 0) + 1
                st.session_state[f"{session_prefix}_{index}_contabilizado"] = True

        with st.expander("📖 Ver explicação e referências", expanded=False):
            st.markdown(f"""
            <div class="explicacao-box">
                {questao.explicacao}
            </div>
            """, unsafe_allow_html=True)

            refs = getattr(questao, "referencias", [])
            if refs:
                st.markdown("#### 📌 Onde estudar este conteúdo:")
                refs_html = "".join([
                    f'<span style="display:inline-block; background:rgba(139,92,246,0.18); '
                    f'border:1px solid rgba(139,92,246,0.45); border-radius:8px; '
                    f'padding:0.25rem 0.75rem; margin:3px; font-size:0.85rem; color:#c4b5fd;">'
                    f'📎 {ref}</span>'
                    for ref in refs
                ])
                st.markdown(f'<div style="margin-top:0.5rem">{refs_html}</div>', unsafe_allow_html=True)

            st.caption(f"📚 {questao.materia} → {questao.assunto}")

    st.divider()
