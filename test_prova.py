from app.agents.banca_agent import get_banca_agent
from app.agents.prova_agent import get_prova_agent
from app.config import settings

def main():
    print("Iniciando testes da Etapa 7: Analisador de Banca e Prova...\n")
    
    # Teste do Agente de Banca
    nome_banca = "Fundação Getulio Vargas (FGV)"
    print(f"=== TESTANDO AGENTE DA BANCA: {nome_banca} ===")
    
    banca_agent = get_banca_agent()
    resposta_banca = banca_agent.run(nome_banca)
    analise_b = resposta_banca.content
    
    print(f"Estilo: {analise_b.estilo_enunciados}")
    print(f"Dificuldade: {analise_b.grau_dificuldade}")
    print(f"Formato: {analise_b.formato_questoes}")
    print("Características/Pegadinhas:")
    for carac in analise_b.caracteristicas_frequentes:
        print(f"  - {carac}")
        
    print("\n" + "="*50 + "\n")
    
    # Teste do Agente de Prova
    texto_prova_referencia = """
    QUESTÃO 14 - João, servidor público, subtraiu um computador da repartição valendo-se da facilidade proporcionada 
    pelo seu cargo. O advogado de João alegou estado de necessidade, visto que o filho de João estava doente. 
    Com base no Código Penal, julgue a situação:
    A) Trata-se de furto simples, não se configurando peculato.
    B) A ação caracteriza peculato-furto, não sendo aceitável a excludente alegada.
    """
    
    print("=== TESTANDO AGENTE DE PROVA (Exemplo de Questão) ===")
    prova_agent = get_prova_agent()
    resposta_prova = prova_agent.run(texto_prova_referencia)
    analise_p = resposta_prova.content
    
    print(f"Estrutura: {analise_p.estrutura_questoes}")
    print(f"Linguagem: {analise_p.linguagem}")
    print("Tipos de Raciocínio:")
    for raciocinio in analise_p.tipos_raciocinio:
        print(f"  - {raciocinio}")
        
if __name__ == "__main__":
    main()
