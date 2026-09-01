import { clearState, clearToken, loadToken, saveToken } from "./storage";
import type { AnaliseBanca, AnaliseProva, Edital, ListaQuestoes } from "./types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getErrorMessage(raw: string, status: number) {
  try {
    const data = JSON.parse(raw);
    const detail = (data as any)?.detail;
    if (typeof detail === "string" && detail.trim()) {
      if (status === 429) return `Cota da chave API atingida. ${detail}`;
      return detail;
    }
    return JSON.stringify(data);
  } catch {
    return raw || `HTTP ${status}`;
  }
}

async function apiFetch(path: string, init?: RequestInit) {
  const token = loadToken();
  const headers = new Headers(init?.headers || {});
  headers.set("Accept", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    if (res.status === 401) {
      clearToken();
      clearState();
      window.location.href = "/login";
      throw new Error("Sessão expirada. Faça login novamente.");
    }
    const raw = await res.text();
    throw new Error(getErrorMessage(raw, res.status));
  }
  return res;
}

export async function login(email: string, password: string) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ email, password })
  });
  if (!res.ok) {
    const raw = await res.text();
    throw new Error(getErrorMessage(raw, res.status));
  }
  const data = (await res.json()) as { access_token: string };
  saveToken(data.access_token);
}

export async function analyzeBanca(nome_banca: string): Promise<AnaliseBanca> {
  const res = await apiFetch("/analyze/banca", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome_banca })
  });
  return (await res.json()) as AnaliseBanca;
}

export async function analyzeEdital(texto?: string, arquivo?: File): Promise<Edital> {
  const form = new FormData();
  if (texto) form.append("texto", texto);
  if (arquivo) form.append("arquivo", arquivo);
  const res = await apiFetch("/analyze/edital", { method: "POST", body: form });
  return (await res.json()) as Edital;
}

export async function analyzeProva(texto?: string, arquivo?: File): Promise<AnaliseProva> {
  const form = new FormData();
  if (texto) form.append("texto", texto);
  if (arquivo) form.append("arquivo", arquivo);
  const res = await apiFetch("/analyze/prova", { method: "POST", body: form });
  return (await res.json()) as AnaliseProva;
}

export async function generateQuestions(body: any): Promise<ListaQuestoes> {
  const res = await apiFetch("/questions/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  return (await res.json()) as ListaQuestoes;
}

export async function generateQuestionsWithImages(params: {
  materia: string;
  assunto: string;
  dificuldade: string;
  num_alternativas: number;
  images: File[];
  analise_banca?: AnaliseBanca | null;
  analise_prova?: AnaliseProva | null;
  edital?: Edital | null;
}): Promise<ListaQuestoes> {
  const form = new FormData();
  form.append("materia", params.materia);
  form.append("assunto", params.assunto);
  form.append("dificuldade", params.dificuldade);
  form.append("num_alternativas", String(params.num_alternativas));
  if (params.analise_banca) form.append("analise_banca_json", JSON.stringify(params.analise_banca));
  if (params.analise_prova) form.append("analise_prova_json", JSON.stringify(params.analise_prova));
  if (params.edital) form.append("edital_json", JSON.stringify(params.edital));
  for (const img of params.images) form.append("images", img);
  const res = await apiFetch("/questions/generate-with-images", { method: "POST", body: form });
  return (await res.json()) as ListaQuestoes;
}

export async function analyzeProvaFigures(arquivo: File): Promise<{
  ratio: number;
  total_questoes: number;
  total_figuras: number;
  figuras: string[];
}> {
  const form = new FormData();
  form.append("arquivo", arquivo);
  const res = await apiFetch("/analyze/prova-figures", { method: "POST", body: form });
  return (await res.json()) as any;
}

export async function completeQuestion(body: any): Promise<ListaQuestoes> {
  const res = await apiFetch("/questions/complete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  return (await res.json()) as ListaQuestoes;
}

export async function createUser(email: string, password: string, is_admin: boolean = false) {
  const res = await apiFetch("/auth/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, is_admin })
  });
  return await res.json();
}
