# 🎓 ConcursoAI – Agente de Estudos para Concursos Públicos

Plataforma inteligente de estudos baseada em IA (Google Gemini + Agno) para gerar questões inéditas de múltipla escolha com base no conteúdo programático do seu edital.

---

## 🚀 Como Instalar e Executar

### 1. Pré-requisitos

- Python 3.10+ instalado
- Uma chave de API do Google Gemini (obtenha em [aistudio.google.com](https://aistudio.google.com/app/apikey))

### 2. Clone ou baixe o projeto

```bash
# Se usar Git:
git clone <url-do-repositorio>
cd projeto-concurso
```

### 3. Crie e ative o ambiente virtual

```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Configure a chave da API

Copie o arquivo `.env.example` para `.env` e preencha sua chave:

```bash
copy .env.example .env
```

Abra o arquivo `.env` e edite:
```
GOOGLE_API_KEY=AIzaSy...sua_chave_aqui
```

### 6. Execute a aplicação

```powershell
.\.venv\Scripts\streamlit.exe run app\ui\main_ui.py
```

A aplicação abrirá automaticamente no seu navegador em `http://localhost:8501`.

---

## 🧩 Estrutura do Projeto

```
projeto_concurso/
│
├── app/
│   ├── agents/
│   │   ├── edital_agent.py      # Analisa e estrutura o conteúdo do edital
│   │   ├── banca_agent.py       # Carrega o perfil da banca organizadora
│   │   ├── prova_agent.py       # Analisa o estilo de uma prova anterior
│   │   └── questoes_agent.py    # Gera questões inéditas (agente principal)
│   │
│   ├── models/
│   │   └── schemas.py           # Modelos Pydantic (Edital, Questao, etc.)
│   │
│   ├── ui/
│   │   ├── main_ui.py           # Interface principal (Streamlit)
│   │   └── components.py        # Componentes de UI reutilizáveis
│   │
│   └── config/
│       └── settings.py          # Carregamento de variáveis de ambiente
│
├── uploads/                     # Futuros uploads de PDF
├── tests/                       # Testes automatizados
├── .env                         # Chaves de API (não subir ao Git!)
├── .env.example                 # Modelo de variáveis de ambiente
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🤖 Agentes de IA

| Agente | Responsabilidade |
|--------|-----------------|
| `edital_agent` | Recebe texto bruto do edital e organiza em Matérias > Assuntos > Tópicos |
| `banca_agent` | Pesquisa o perfil histórico de uma banca (dificuldade, estilo, pegadinhas) |
| `prova_agent` | Analisa o estilo de cobrança de uma prova anterior |
| `questoes_agent` | Combina todos os contextos e gera questões inéditas validadas pelo Pydantic |

---

## 🛡️ Boas Práticas de Segurança

- A chave `GOOGLE_API_KEY` **nunca** é commitada no repositório (protegida pelo `.gitignore`)
- O sistema valida a presença da chave na inicialização
- Todas as respostas da IA passam por validação Pydantic antes de serem exibidas

---

## 📋 Funcionalidades

- [x] Análise automática do conteúdo programático do edital
- [x] Perfil da banca organizadora com estilo e dificuldade
- [x] Análise de prova de referência (opcional)
- [x] Geração de questões inéditas com gabarito e explicação
- [x] Interface gráfica com tema dark moderno
- [x] Sistema de simulado com seleção de respostas
- [x] Placar de desempenho da sessão
- [ ] Upload de edital em PDF (em desenvolvimento)
- [ ] Histórico de desempenho por matéria e gráficos
- [ ] Exportação de relatório PDF
