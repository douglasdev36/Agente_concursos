from pydantic import BaseModel, Field
from typing import List, Optional

class Topico(BaseModel):
    nome: str = Field(..., description="Nome do tópico ou subassunto específico.")

class Assunto(BaseModel):
    nome: str = Field(..., description="Nome do assunto principal.")
    topicos: List[Topico] = Field(default_factory=list, description="Lista de tópicos ou subassuntos dentro deste assunto.")

class Materia(BaseModel):
    nome: str = Field(..., description="Nome da disciplina ou matéria (Ex: Português, Matemática).")
    assuntos: List[Assunto] = Field(default_factory=list, description="Lista de assuntos que compõem a matéria.")

class Edital(BaseModel):
    materias: List[Materia] = Field(default_factory=list, description="Lista de todas as matérias extraídas do edital.")

class AnaliseBanca(BaseModel):
    estilo_enunciados: str = Field(..., description="Descrição sobre como a banca formula os enunciados (ex: longos, diretos, casos práticos).")
    grau_dificuldade: str = Field(..., description="Grau de dificuldade geral esperado (Fácil, Médio, Difícil).")
    formato_questoes: str = Field(..., description="Múltipla escolha (A-E, A-D) ou Certo/Errado.")
    caracteristicas_frequentes: List[str] = Field(default_factory=list, description="Lista de pegadinhas comuns ou características marcantes da banca.")

class AnaliseProva(BaseModel):
    estrutura_questoes: str = Field(..., description="Como as questões da prova referência são estruturadas (tamanho, complexidade).")
    linguagem: str = Field(..., description="Tipo de linguagem utilizada (técnica, coloquial, jurídica).")
    tipos_raciocinio: List[str] = Field(default_factory=list, description="Quais tipos de raciocínio a prova exigiu (interpretação profunda, decoreba, cálculo).")

class Alternativa(BaseModel):
    letra: str = Field(..., description="Letra da alternativa: A, B, C, D ou E.")
    texto: str = Field(..., description="Texto completo da alternativa.")

class Questao(BaseModel):
    numero: int = Field(..., description="Número sequencial da questão.")
    texto_base: Optional[str] = Field(default=None, description="Texto base para interpretação/análise, quando aplicável. Se presente, o enunciado deve se referir a ele.")
    titulo_texto_base: Optional[str] = Field(default=None, description="Título/identificador do texto base (ex: 'Texto I'), quando aplicável.")
    figura_key: Optional[str] = Field(default=None, description="Chave de referência para uma figura/diagrama anexado na interface. Usado apenas pelo app para renderização.")
    enunciado: str = Field(..., description="Texto completo do enunciado da questão.")
    alternativas: List[Alternativa] = Field(..., description="Lista com as alternativas da questão (A, B, C, D, E).")
    resposta_correta: str = Field(..., description="Letra da alternativa correta (ex: 'A', 'B', 'C').")
    explicacao: str = Field(..., description="Explicação detalhada do por que a resposta correta é correta e por que as demais estão erradas.")
    referencias: List[str] = Field(default_factory=list, description="Lista de referências para estudo: artigos de lei, súmulas, jurisprudência, capítulos de doutrina. Ex: 'Art. 5º, XI da CF/88', 'Súmula 231 do STJ'.")
    materia: str = Field(..., description="Nome da matéria a qual a questão pertence.")
    assunto: str = Field(..., description="Nome do assunto específico abordado na questão.")
    dificuldade: str = Field(..., description="Nível de dificuldade da questão: Fácil, Médio, Difícil ou Avançado.")

class ListaQuestoes(BaseModel):
    questoes: List[Questao] = Field(default_factory=list, description="Lista de todas as questões geradas.")
