export type Alternativa = {
  letra: string;
  texto: string;
};

export type Questao = {
  numero: number;
  texto_base?: string | null;
  titulo_texto_base?: string | null;
  figura_key?: string | null;
  enunciado: string;
  alternativas: Alternativa[];
  resposta_correta: string;
  explicacao: string;
  referencias: string[];
  materia: string;
  assunto: string;
  dificuldade: string;
};

export type ListaQuestoes = {
  questoes: Questao[];
};

export type Edital = {
  materias: Array<{
    nome: string;
    assuntos: Array<{
      nome: string;
      topicos: Array<{ nome: string }>;
    }>;
  }>;
};

export type AnaliseBanca = {
  estilo_enunciados: string;
  grau_dificuldade: string;
  formato_questoes: string;
  caracteristicas_frequentes: string[];
};

export type AnaliseProva = {
  estrutura_questoes: string;
  linguagem: string;
  tipos_raciocinio: string[];
};

export type BlocoQuestoes = {
  label: string;
  dificuldade: string;
  questoes: Questao[];
};

