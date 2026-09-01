import type { AnaliseBanca, AnaliseProva, BlocoQuestoes, Edital } from "./types";

const KEY = "concursoai_state_v1";

export type StoredState = {
  edital?: Edital | null;
  analise_banca?: AnaliseBanca | null;
  analise_prova?: AnaliseProva | null;
  prova_figuras_ratio?: number | null;
  prova_figuras_pool?: string[] | null;
  blocos?: BlocoQuestoes[];
  respostas?: Record<string, string>;
  figuras?: Record<string, string>;
};

export function loadState(): StoredState {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return {};
    return JSON.parse(raw) as StoredState;
  } catch {
    return {};
  }
}

export function saveState(patch: StoredState) {
  const current = loadState();
  const next = { ...current, ...patch };
  localStorage.setItem(KEY, JSON.stringify(next));
}

export function clearState() {
  localStorage.removeItem(KEY);
}

const TOKEN_KEY = "concursoai_token";

export function loadToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function saveToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}
