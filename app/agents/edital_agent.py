from agno.agent import Agent
from agno.models.google import Gemini
from app.models.schemas import Edital

def get_edital_agent() -> Agent:
    """
    Retorna o agente configurado especificamente para analisar e 
    estruturar conteúdos programáticos de editais.
    """
    return Agent(
        model=Gemini(id="gemini-3.6-flash"),
        description="Você é um especialista em análise de editais de concursos públicos.",
        instructions=[
            "Seu objetivo é receber um texto bruto contendo o conteúdo programático de um edital e organizá-lo.",
            "Extraia todas as matérias, seus respectivos assuntos e tópicos/subassuntos de forma hierárquica.",
            "Ignore textos que não façam parte do conteúdo programático (como regras do concurso, horários, etc).",
            "Mantenha os nomes originais dos assuntos conforme o edital fornecido."
        ],
        output_schema=Edital, # Força o agente a responder no formato Pydantic definido
        structured_outputs=True, # Garante que a saída seja um JSON válido e parseado
        markdown=False
    )
