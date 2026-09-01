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
            "O usuário fornecerá o nome de uma banca organizadora.",
            "Baseado em seu vasto conhecimento, você deve descrever detalhadamente o perfil dessa banca.",
            "Descreva o estilo dos enunciados, o nível de dificuldade, o formato típico das questões (Certo/Errado ou A,B,C,D,E) e as pegadinhas mais comuns."
        ],
        output_schema=AnaliseBanca,
        structured_outputs=True,
        markdown=False
    )
