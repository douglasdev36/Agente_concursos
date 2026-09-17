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
            "Seu objetivo é receber um texto de edital ou tópicos de conteúdo programático e organizá-lo no formato estruturado solicitado.",
            "Extraia e agrupe todo o conteúdo na lista obrigatória 'materias'. Cada matéria deve conter 'nome' e a lista 'assuntos'.",
            "Mesmo que o texto fornecido seja apenas um trecho ou não traga cabeçalhos formais de matéria (ex: venha apenas 'Estatística básica: ...' ou '8. Matemática financeira: ...'), deduza e crie a Matéria apropriada (ex: 'Matemática e Estatística', 'Conhecimentos Específicos').",
            "NUNCA retorne a lista de matérias vazia se houver tópicos e conteúdos no texto fornecido.",
            "Ignore textos administrativos que não façam parte do conteúdo programático (como prazos, horários, taxas).",
            "Retorne apenas o JSON correspondente ao esquema, sem comentários externos."
        ],
        output_schema=Edital, # Força o agente a responder no formato Pydantic definido
        structured_outputs=True, # Garante que a saída seja um JSON válido e parseado
        markdown=False
    )
