from agno.agent import Agent
from agno.models.google import Gemini
from app.models.schemas import AnaliseBanca

def get_banca_agent() -> Agent:
    """
    Retorna o agente responsável por analisar o nome/histórico de uma banca
    e extrair o seu perfil e padrão de cobrança.
    """
    return Agent(
        model=Gemini(id="gemini-3.6-flash"),
        description="Você é um especialista em bancas de concursos públicos brasileiros (ex: Cebraspe, FGV, Vunesp, FCC).",
        instructions=[
            "O usuário fornecerá o nome de uma banca examinadora de concurso público (ex: Cesgranrio, Cebraspe, FGV, Vunesp, FCC).",
            "Descreva detalhadamente o perfil dessa banca atendendo estritamente aos campos do esquema:",
            "- estilo_enunciados: estilo de cobrança e tamanho dos enunciados;",
            "- grau_dificuldade: nível geral (ex: Fácil, Médio, Difícil);",
            "- formato_questoes: formato usual (ex: Múltipla escolha (A-E) ou Certo/Errado);",
            "- caracteristicas_frequentes: lista com pegadinhas comuns e características marcantes da banca.",
            "Retorne apenas o JSON correspondente ao esquema, sem comentários antes ou depois."
        ],
        output_schema=AnaliseBanca,
        structured_outputs=True,
        markdown=False
    )
