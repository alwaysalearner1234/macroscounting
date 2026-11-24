"use client";

/** Typed fetch boundary for the FastAPI application. */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
  user: { id: number; email: string };
}

export interface ScoutingMetrics {
  matches: number;
  gd_at_15: number;
  fb_rate: number;
  ft_rate: number;
  objective_capture_rates: Record<string, number>;
  jungle_pathing_0_5: Array<{ match_id: string; team: string; x: number; y: number; minute: number }>;
  pre_objective_ward_coordinates: Array<{ match_id: string; team: string; x: number; y: number; objective?: string }>;
}

export interface CoachBriefResponse {
  opponent_team: string;
  brief: string;
  verified_metrics: ScoutingMetrics;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (typeof window !== "undefined") {
    const token = window.localStorage.getItem("c9_access_token");
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `API request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const result = await request<TokenResponse>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
  if (typeof window !== "undefined") window.localStorage.setItem("c9_access_token", result.access_token);
  return result;
}

export function requestCoachBrief(opponent_team: string, question: string): Promise<CoachBriefResponse> {
  return request<CoachBriefResponse>("/coach/brief", { method: "POST", body: JSON.stringify({ opponent_team, question }) });
}

export function uploadScoutingMatches(opponent_team: string, matches: unknown[]) {
  return request(`/scouting/reports`, { method: "PUT", body: JSON.stringify({ opponent_team, matches }) });
}