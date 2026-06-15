export type Budget = "low" | "medium" | "high";

export interface RecommendationRequest {
  location: string;
  budget: Budget;
  cuisine: string;
  min_rating: number;
  additional_preferences?: string | null;
  top_k: number;
}

export interface Restaurant {
  id: string;
  name: string;
  location: string;
  cuisines: string[];
  rating: number;
  estimated_cost: number | null;
  budget_band: Budget | null;
  metadata: Record<string, unknown>;
}

export interface Recommendation {
  rank: number;
  restaurant: Restaurant;
  explanation: string;
}

export interface RecommendationResponse {
  summary: string | null;
  recommendations: Recommendation[];
  meta: {
    status?: string;
    message?: string;
    llm_fallback?: boolean;
    candidates_considered?: number;
    candidates_sent_to_llm?: number;
    llm_latency_ms?: number;
    filter_ms?: number;
    llm_model?: string;
    correlation_id?: string;
  };
}

export interface FormState {
  areaPick: string;
  customArea: string;
  budget: Budget;
  cuisineMode: "pick" | "custom";
  cuisinePick: string;
  cuisineCustom: string;
  minRating: number;
  topK: number;
  additionalPreferences: string;
}

export type AppStatus = "idle" | "loading" | "success" | "empty" | "error";
