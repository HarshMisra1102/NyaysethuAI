import { auth } from "@/lib/auth";
import type { AuthResponse, Case, ChatResponse, DocumentUploadResponse, RightsResponse, RTIDraft, SchemeResponse, User } from "@/types";
const BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
export class ApiError extends Error { constructor(public status: number, message: string) { super(message); } }
async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers); const token = auth.token();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  let response: Response;
  try { response = await fetch(`${BASE_URL}/api/v1${path}`, { ...init, headers }); }
  catch { throw new ApiError(503, "Unable to reach NyayaSetu. Please check your connection and try again."); }
  if (response.status === 401) { auth.clear(); if (typeof window !== "undefined" && !location.pathname.startsWith("/login")) location.assign("/login?expired=1"); throw new ApiError(401, "Your session has expired. Please sign in again."); }
  if (!response.ok) { const body: unknown = await response.json().catch(() => null); const detail = body && typeof body === "object" && "detail" in body ? String(body.detail) : "Something went wrong. Please try again."; throw new ApiError(response.status, detail); }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
export const api = {
  register: (body: { name: string; email: string; password: string; state?: string; district?: string }) => request<AuthResponse>("/auth/register", { method: "POST", body: JSON.stringify(body) }),
  login: (body: { email: string; password: string }) => request<AuthResponse>("/auth/login", { method: "POST", body: JSON.stringify(body) }),
  me: () => request<User>("/auth/me"), cases: () => request<Case[]>("/cases"),
  case: (id: number) => request<Case>(`/cases/${id}`), createCase: (body: { title: string; category: string; description: string }) => request<Case>("/cases", { method: "POST", body: JSON.stringify(body) }),
  deleteCase: (id: number) => request<void>(`/cases/${id}`, { method: "DELETE" }),
  chat: (body: { case_id: number; message: string }) => request<ChatResponse>("/chat/query", { method: "POST", body: JSON.stringify(body) }),
  upload: (file: File) => { const body = new FormData(); body.append("file", file); return request<DocumentUploadResponse>("/documents/upload", { method: "POST", body }); },
  rights: (body: { problem: string; category?: string; state?: string; district?: string }) => request<RightsResponse>("/rights/analyze", { method: "POST", body: JSON.stringify(body) }),
  rti: (body: { question: string; state?: string; district?: string; applicant_name?: string; applicant_address?: string }) => request<RTIDraft>("/rti/draft", { method: "POST", body: JSON.stringify(body) }),
  schemes: (body: { scheme_name?: string; age?: number; state?: string; district?: string; occupation?: string; annual_income?: number; category?: string }) => request<SchemeResponse>("/schemes/eligibility", { method: "POST", body: JSON.stringify(body) }),
  health: async () => { const response = await fetch(`${BASE_URL}/api/v1/health`); return response.ok; }
};
