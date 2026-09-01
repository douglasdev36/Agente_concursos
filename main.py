import os
from agno.agent import Agent
from agno.models.google import Gemini

# Importa as configurações, o que já executa a verificação da chave de API
from app.config import settings

def main():
    print("Iniciando teste de comunicação Agno + Gemini...")
    
    # Verifica se a chave é o dummy do ambiente recém-criado
    if settings.GEMINI_API_KEY == "dummy_key_for_now":
        print("\n[AVISO] Você está usando a chave dummy 'dummy_key_for_now' no arquivo .env.")
        print("Para que a chamada à API funcione de verdade, substitua por uma chave real do Google Gemini.\n")
    
    try:
        # Instancia o agente do Agno com o modelo Gemini
        agent = Agent(
            model=Gemini(id="gemini-3.6-flash"), 
            description="Você é um assistente útil e direto.",
            markdown=True
        )
        
        print("Agente configurado com sucesso! Enviando prompt de teste...\n")
        
        # Envia a mensagem e obtém a resposta (usamos print_response para exibir no terminal)
        # Como a chave é dummy, isso provavelmente falhará se tentar executar agora, 
        # mas o código de integração está correto e estruturado.
        agent.print_response("Olá! Responda apenas com: 'Comunicação bem-sucedida!'", stream=True)
        
    except Exception as e:
        print(f"\nOcorreu um erro durante a comunicação com a API: {e}")

if __name__ == "__main__":
    main()
