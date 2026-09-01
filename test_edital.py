from app.agents.edital_agent import get_edital_agent
from app.config import settings

def main():
    print("Iniciando teste do Analisador de Edital...\n")
    
    texto_edital_bruto = """
    Língua Portuguesa: 1 Compreensão e interpretação de textos. 2 Tipologia textual. 3 Ortografia oficial. 4 Acentuação gráfica. 
    Raciocínio Lógico: 1 Estruturas lógicas. 2 Lógica de argumentação.
    Conhecimentos Específicos - Direito Constitucional: 1 Constituição: conceito, classificações, princípios fundamentais. 2 Direitos e garantias fundamentais.
    """
    
    print("Texto fornecido para o Agente:")
    print(texto_edital_bruto)
    print("-" * 50)
    
    agent = get_edital_agent()
    print("Analisando e estruturando (isso pode levar alguns segundos)...\n")
    
    # O response_model garante que a resposta será um objeto Edital do Pydantic
    resposta = agent.run(texto_edital_bruto)
    
    edital_estruturado = resposta.content
    
    print("=== RESULTADO DA ESTRUTURAÇÃO ===")
    for materia in edital_estruturado.materias:
        print(f"Materia: {materia.nome}")
        for assunto in materia.assuntos:
            print(f"  |- Assunto: {assunto.nome}")
            for topico in assunto.topicos:
                print(f"  |  |- Topico: {topico.nome}")
        print("")

if __name__ == "__main__":
    main()
