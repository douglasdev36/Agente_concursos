import os
import sys
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

def check_env():
    """Verifica se a chave da API do Gemini está configurada."""
    if not GEMINI_API_KEY:
        print("ERRO CRÍTICO: A variável GOOGLE_API_KEY não foi encontrada no arquivo .env!")
        print("Por favor, crie um arquivo .env na raiz do projeto (use o .env.example como base) e adicione a sua chave.")
        sys.exit(1)

check_env()
