from agno.agent import Agent
from agno.models.google import Gemini
from app.models.schemas import AnaliseProva

def get_prova_agent() -> Agent:
    """
    Retorna o agente responsável por ler o texto de uma prova anterior
    e identificar a estrutura, linguagem e complexidade.
    """
    return Agent(
        model=Gemini(id="gemini-3.6-flash"),
        description="Você é um especialista em engenharia reversa de provas de concursos públicos.",
        instructions=[
            "O usuário fornecerá o texto bruto de uma prova anterior (geralmente extraído de PDF ou imagem OCR).",
            "Sua tarefa é analisar esse texto APENAS para identificar o estilo de cobrança, não é para resolver a prova.",
            "Identifique a estrutura média das questões (se os textos de apoio são longos ou curtos), a linguagem (técnica, rebuscada, simples) e que tipos de raciocínio foram cobrados."
        ],
        output_schema=AnaliseProva,
        structured_outputs=True,
        markdown=False
    )
