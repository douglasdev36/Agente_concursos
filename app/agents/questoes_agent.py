from typing import Optional, Sequence, Tuple, List
from agno.agent import Agent
from agno.models.google import Gemini
from agno.media import Image
from app.models.schemas import ListaQuestoes, AnaliseBanca, AnaliseProva, Edital


def _construir_contexto_banca(analise_banca: Optional[AnaliseBanca]) -> str:
    """Formata os dados da banca em texto para uso no prompt."""
    if not analise_banca:
        return "Nenhuma informação sobre a banca disponível. Gere questões em nível médio."
    
    caracteristicas = "\n".join([f"- {c}" for c in analise_banca.caracteristicas_frequentes])
    return (
        f"Estilo dos enunciados: {analise_banca.estilo_enunciados}\n"
        f"Grau de dificuldade: {analise_banca.grau_dificuldade}\n"
        f"Formato: {analise_banca.formato_questoes}\n"
        f"Características e pegadinhas comuns:\n{caracteristicas}"
    )


def _construir_contexto_prova(analise_prova: Optional[AnaliseProva]) -> str:
    """Formata os dados da prova de referência em texto para uso no prompt."""
    if not analise_prova:
        return "Nenhuma prova de referência fornecida."
    
    tipos = "\n".join([f"- {t}" for t in analise_prova.tipos_raciocinio])
    return (
        f"Estrutura das questões: {analise_prova.estrutura_questoes}\n"
        f"Linguagem: {analise_prova.linguagem}\n"
        f"Tipos de raciocínio exigidos:\n{tipos}"
    )


def _construir_contexto_edital(edital: Optional[Edital], materia: str, assunto: str) -> str:
    """Resume o conteúdo autorizado do edital para a questão em questão."""
    if not edital:
        return f"Matéria: {materia}\nAssunto: {assunto}"
    
    # Procura a matéria e assunto no edital estruturado
    for mat in edital.materias:
        if materia.lower() in mat.nome.lower():
            for ass in mat.assuntos:
                if assunto.lower() in ass.nome.lower():
                    topicos = ", ".join([t.nome for t in ass.topicos]) if ass.topicos else "Todos os tópicos do assunto"
                    return (
                        f"Matéria: {mat.nome}\n"
                        f"Assunto: {ass.nome}\n"
                        f"Tópicos autorizados: {topicos}"
                    )
    return f"Matéria: {materia}\nAssunto: {assunto}"


def get_questoes_agent(
    analise_banca: Optional[AnaliseBanca] = None,
    analise_prova: Optional[AnaliseProva] = None,
    edital: Optional[Edital] = None,
) -> Agent:
    """
    Retorna o agente gerador de questões, já configurado com todo o contexto
    disponível (banca, prova de referência e edital).
    """
    contexto_banca = _construir_contexto_banca(analise_banca)
    contexto_prova = _construir_contexto_prova(analise_prova)

    return Agent(
        model=Gemini(id="gemini-3.6-flash"),
        description="Você é um elaborador especialista em questões de múltipla escolha para concursos públicos brasileiros.",
        instructions=[
            "Você deve criar questões de múltipla escolha INÉDITAS com base APENAS no conteúdo programático informado.",
            "NUNCA reproduza questões existentes de provas anteriores. Use a prova de referência apenas como inspiração de estilo.",
            "Cada questão DEVE ter exatamente 5 alternativas (A, B, C, D, E).",
            "As alternativas incorretas devem ser PLAUSÍVEIS e relacionadas ao conteúdo, evitando distratores obviamente errados.",
            "A explicação deve justificar POR QUE a alternativa correta está certa E por que cada incorreta está errada, de forma didática e detalhada.",
            "OBRIGATÓRIO: Preencha o campo 'referencias' com as fontes precisas do conteúdo cobrado na questão. Exemplos:",
            "  - Para Direito: 'Art. 5º, XI da CF/88', 'Súmula 231 do STJ', 'RE 603.616 – STF (Tema 280)'",
            "  - Para Português: 'Nova Ortografia – Acordo Ortográfico de 1990', 'Gramática Houaiss – Concordância Verbal'",
            "  - Para Matemática: 'Teorema de Pitágoras', 'Progressão Aritmética – fórmula do termo geral'",
            "  - Para Administrativa: 'Lei 8.112/90, Art. 117', 'Decreto 9.991/2019'",
            "  Inclua pelo menos 1 referência por questão, preferencialmente 2 a 3.",
            "DIRETRIZ PARA EXATAS/ENGENHARIA:",
            "  - Para questões de Engenharia Elétrica, Física ou Matemática que normalmente precisariam de imagens, use DESCRIÇÕES TEXTUAIS PRECISAS.",
            "  - Quando útil, utilize 'ASCII Art' simples ou blocos de código formatados dentro do enunciado para representar esquemas.",
            "  - Exemplos de esquemas aceitos: diagrama unifilar, circuitos em Estrela (Y) e Triângulo (Δ), diagrama de blocos de automação, lógica ladder (LD) em forma textual, I/O list, tabelas de endereçamento (I0.0, Q0.0, M0.0), P&ID simplificado em texto, diagramas de temporização, e tabelas de bornes.",
            "  - Para desenhos técnicos, use tabelas com medidas/dimensões, tolerâncias, vistas (frontal/superior/lateral) descritas em texto e, quando fizer sentido, representações ASCII de geometria simples.",
            "  - Utilize tabelas Markdown para apresentar dados de ensaios ou coordenadas de gráficos.",
            "Siga RIGOROSAMENTE o estilo e o nível de dificuldade do perfil da banca fornecido.",
            "",
            f"=== PERFIL DA BANCA ===\n{contexto_banca}",
            "",
            f"=== ESTILO DA PROVA DE REFERÊNCIA ===\n{contexto_prova}",
        ],
        output_schema=ListaQuestoes,
        structured_outputs=True,
        markdown=False
    )


def gerar_questoes(
    materia: str,
    assunto: str,
    quantidade: int,
    dificuldade: str,
    nivel_ensino: Optional[str] = None,
    num_alternativas: int = 5,
    incluir_texto_base: bool = False,
    modo_texto_base: Optional[str] = None,
    texto_base_fornecido: Optional[str] = None,
    analise_banca: Optional[AnaliseBanca] = None,
    analise_prova: Optional[AnaliseProva] = None,
    edital: Optional[Edital] = None,
) -> ListaQuestoes:
    """
    Orquestra a geração de questões combinando todo o contexto disponível.

    Args:
        materia: Nome da matéria (ex: "Direito Constitucional")
        assunto: Nome do assunto específico (ex: "Direitos Fundamentais")
        quantidade: Número de questões a gerar
        dificuldade: Nível de dificuldade ("Fácil", "Médio", "Difícil", "Avançado", "Estilo da Banca")
        num_alternativas: Número de alternativas (padrão 5, ou 4 para A-D)
        analise_banca: Análise do perfil da banca (opcional)
        analise_prova: Análise da prova de referência (opcional)
        edital: Estrutura do edital analisado (opcional)

    Returns:
        ListaQuestoes: objeto Pydantic contendo as questões geradas
    """
    contexto_edital = _construir_contexto_edital(edital, materia, assunto)

    instr_nivel_ensino = ""
    if nivel_ensino:
        instr_nivel_ensino = (
            "REQUISITO DE NÍVEL DE ENSINO:\n"
            f"- Nível de ensino alvo: {nivel_ensino}\n"
            "- Adeque vocabulário, complexidade, profundidade e tamanho do enunciado a esse nível.\n"
            "- Evite termos avançados sem contextualização quando o nível for Fundamental/Médio.\n"
        )

    instr_texto_base = ""
    if incluir_texto_base:
        if modo_texto_base == "fornecido" and texto_base_fornecido:
            instr_texto_base = (
                "REQUISITO DE TEXTO BASE:\n"
                "- Use exatamente o TEXTO BASE FORNECIDO abaixo e copie-o para o campo 'texto_base' de TODAS as questões.\n"
                "- Preencha também o campo 'titulo_texto_base' com 'Texto I'.\n"
                "- O campo 'enunciado' deve se referir ao texto_base (ex: 'Com base no Texto I, assinale...').\n\n"
                f"=== TEXTO BASE FORNECIDO ===\n{texto_base_fornecido}\n"
            )
        else:
            instr_texto_base = (
                "REQUISITO DE TEXTO BASE:\n"
                "- Para CADA questão, crie um texto inédito em português (entre 120 e 250 palavras) e preencha o campo 'texto_base'.\n"
                "- Preencha também o campo 'titulo_texto_base' (ex: 'Texto I', 'Texto II', etc.).\n"
                "- O campo 'enunciado' deve se referir ao texto_base (ex: 'Com base no Texto I, assinale...').\n"
            )

    prompt = (
        f"Gere exatamente {quantidade} questão(ões) de múltipla escolha com {num_alternativas} alternativas.\n"
        f"Dificuldade solicitada: {dificuldade}\n\n"
        f"=== CONTEÚDO AUTORIZADO DO EDITAL ===\n{contexto_edital}\n\n"
        f"{instr_nivel_ensino}\n"
        f"{instr_texto_base}\n"
        f"IMPORTANTE: As questões devem cobrir APENAS o conteúdo especificado acima. "
        f"Numere as questões sequencialmente a partir de 1."
    )

    agent = get_questoes_agent(analise_banca, analise_prova, edital)
    resposta = agent.run(prompt)
    return resposta.content


def gerar_questoes_com_imagens(
    materia: str,
    assunto: str,
    imagens: Sequence[Tuple[bytes, str]],
    dificuldade: str,
    num_alternativas: int = 5,
    analise_banca: Optional[AnaliseBanca] = None,
    analise_prova: Optional[AnaliseProva] = None,
    edital: Optional[Edital] = None,
) -> ListaQuestoes:
    contexto_edital = _construir_contexto_edital(edital, materia, assunto)
    agent = get_questoes_agent(analise_banca, analise_prova, edital)

    questoes = []
    for img_bytes, mime_type in imagens:
        prompt = (
            f"Gere exatamente 1 questão(ão) de múltipla escolha com {num_alternativas} alternativas.\n"
            f"Dificuldade solicitada: {dificuldade}\n\n"
            f"=== CONTEÚDO AUTORIZADO DO EDITAL ===\n{contexto_edital}\n\n"
            "A IMAGEM ANEXADA contém um diagrama/figura que deve ser usada como base da questão.\n"
            "- Crie um enunciado que dependa diretamente da interpretação do diagrama.\n"
            "- Priorize casos típicos de Engenharia/Automação: diagrama unifilar, esquema de comando/potência, ladder, diagrama de blocos, instrumentação e P&ID, desenhos técnicos com cotas e vistas.\n"
            "- No enunciado, faça referência a 'Figura 1'.\n"
            "- Não invente elementos que não estejam visíveis; use apenas o que puder inferir com segurança.\n"
            "Numere a questão a partir de 1."
        )

        resposta = agent.run(
            prompt,
            images=[Image(content=img_bytes, mime_type=mime_type)],
        )
        questoes.extend(resposta.content.questoes)

    return ListaQuestoes(questoes=questoes)


def get_completar_questao_agent(
    analise_banca: Optional[AnaliseBanca] = None,
    analise_prova: Optional[AnaliseProva] = None,
) -> Agent:
    """
    Retorna o agente especializado em gerar alternativas (distratores e gabarito) 
    para um enunciado já existente.
    """
    contexto_banca = _construir_contexto_banca(analise_banca)
    contexto_prova = _construir_contexto_prova(analise_prova)

    return Agent(
        model=Gemini(id="gemini-3.6-flash"),
        description="Você é um especialista em elaborar distratores (alternativas incorretas) e gabaritos perfeitos para questões de concursos públicos.",
        instructions=[
            "O usuário fornecerá o ENUNCIADO de uma questão.",
            "Você deve ler o enunciado, resolver o problema proposto e criar as ALTERNATIVAS seguindo a psicologia de bancas de concurso.",
            "O número de alternativas será especificado no prompt (geralmente 4 ou 5).",
            "REGRAS PARA AS ALTERNATIVAS:",
            "  1. Uma deve ser inquestionavelmente correta.",
            "  2. Uma deve ser uma 'pegadinha' forte (muito plausível, erro sutil ou erro de cálculo comum).",
            "  3. As demais devem ser distratores plausíveis, mas claramente incorretos após análise.",
            "A explicação deve detalhar o erro de cada distrator, especialmente da 'pegadinha'.",
            "Preencha o campo 'referencias' com as fontes precisas do assunto, assim como na geração normal.",
            "Retorne APENAS 1 questão no objeto da lista. O 'enunciado' retornado deve ser uma cópia limpa e bem formatada do enunciado fornecido pelo usuário.",
            "Siga RIGOROSAMENTE o estilo da banca fornecida.",
            "",
            f"=== PERFIL DA BANCA ===\n{contexto_banca}",
            "",
            f"=== ESTILO DA PROVA DE REFERÊNCIA ===\n{contexto_prova}",
        ],
        output_schema=ListaQuestoes,
        structured_outputs=True,
        markdown=False
    )


def completar_questao(
    enunciado: str,
    materia: str,
    assunto: str,
    num_alternativas: int = 5,
    analise_banca: Optional[AnaliseBanca] = None,
    analise_prova: Optional[AnaliseProva] = None,
) -> ListaQuestoes:
    """
    Gera alternativas para um enunciado fornecido pelo usuário.
    """
    prompt = (
        f"Matéria: {materia}\n"
        f"Assunto: {assunto}\n\n"
        f"Gere exatamente {num_alternativas} alternativas (A até {'E' if num_alternativas == 5 else 'D'}) para o seguinte enunciado:\n\n"
        f"=== ENUNCIADO FORNECIDO ===\n{enunciado}\n=========================\n\n"
        f"Lembre-se de retornar uma lista contendo exatamente 1 (uma) Questao, onde o campo 'enunciado' é o próprio enunciado formatado."
    )

    agent = get_completar_questao_agent(analise_banca, analise_prova)
    resposta = agent.run(prompt)
    return resposta.content
