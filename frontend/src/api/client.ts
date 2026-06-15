import type { Recommendation, RecommendationRequest, RecommendationResponse } from "../types";

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "/api/v1").replace(/\/$/, "");

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  const data = await response.json();
  if (!response.ok) {
    const message =
      typeof data?.message === "string" ? data.message : "Request failed. Please try again.";
    throw new Error(message);
  }
  return data as T;
}

export async function fetchAreas(): Promise<string[]> {
  const data = await fetchJson<{ items: string[] }>("/metadata/areas");
  return data.items;
}

export async function fetchCuisines(): Promise<string[]> {
  const data = await fetchJson<{ items: string[] }>("/metadata/cuisines");
  return data.items;
}

export async function fetchRecommendations(
  body: RecommendationRequest,
): Promise<RecommendationResponse> {
  return fetchJson<RecommendationResponse>("/recommendations", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Correlation-ID": crypto.randomUUID().slice(0, 12),
    },
    body: JSON.stringify(body),
  });
}

export function deduplicateRecommendations(recommendations: Recommendation[]): Recommendation[] {
  const seen = new Set<string>();
  return recommendations.filter((entry) => {
    const key = entry.restaurant.name.trim().toLowerCase();
    if (!key || seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}
