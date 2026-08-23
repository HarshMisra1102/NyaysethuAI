import type { AuthResponse, User } from "@/types";
const TOKEN_KEY = "nyayasetu_access_token";
const USER_KEY = "nyayasetu_user";
export const auth = {
  token: () => typeof window === "undefined" ? null : localStorage.getItem(TOKEN_KEY),
  user: (): User | null => { if (typeof window === "undefined") return null; try { const value = localStorage.getItem(USER_KEY); return value ? JSON.parse(value) as User : null; } catch { return null; } },
  save: (data: AuthResponse) => { localStorage.setItem(TOKEN_KEY, data.access_token); localStorage.setItem(USER_KEY, JSON.stringify(data.user)); },
  clear: () => { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); }
};
