from app.agents.banca_agent import get_banca_agent
from app.agents.questoes_agent import gerar_questoes
from app.config import settings

def main():
    print("Iniciando teste do Gerador de Questoes (Etapa 8)...\n")
    print("Passo 1: Carregando perfil da banca Cebraspe...")
    
    # Obtemos o perfil da banca para contextualizar as questões
    banca_agent = get_banca_agent()
    resposta_banca = banca_agent.run("Cebraspe (antigo CESPE)")
    analise_banca = resposta_banca.content
    
    print(f"  Banca: Cebraspe | Dificuldade: {analise_banca.grau_dificuldade}\n")
    print("Passo 2: Gerando questoes de Direito Constitucional...")
    
    lista = gerar_questoes(
        materia="Direito Constitucional",
        assunto="Direitos e Garantias Fundamentais",
        quantidade=2,
        dificuldade="Dificil",
        num_alternativas=5,
        analise_banca=analise_banca,
    )
    
    print(f"\nTotal de questoes geradas: {len(lista.questoes)}\n")
    print("=" * 60)
    
    for questao in lista.questoes:
        print(f"\nQUESTAO {questao.numero} [{questao.dificuldade}]")
        print(f"Materia: {questao.materia} | Assunto: {questao.assunto}")
        print(f"\n{questao.enunciado}\n")
        for alt in questao.alternativas:
            print(f"  {alt.letra}) {alt.texto}")
        print(f"\nGabarito: {questao.resposta_correta}")
        print(f"\nExplicacao:\n{questao.explicacao}")
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
