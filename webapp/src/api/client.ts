import { getInitData } from "../tg";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export interface SearchFilters {
  product_type: "hotel" | "tour" | "both";
  min_stars: number;
  max_price_per_night: number | null;
  max_total_price: number | null;
  max_distance_km: number;
  required_tags: string[];
  sort_by: "relevance" | "price" | "rating";
}

export interface ParsedQuery {
  location: string | null;
  check_in: string | null;
  check_out: string | null;
  budget_max: number | null;
  preferences: string[];
  missing_fields: string[];
  filters?: SearchFilters;
}

export interface HotelResult {
  id: string;
  name: string;
  city: string;
  stars: number;
  price_per_night: number;
  rating: number;
  photo_url: string;
  description: string;
  amenities: string[];
  distance_to_center_km: number;
  tags: string[];
  match_score: number;
  ai_reason: string;
  total_price: number | null;
}

export interface TourResult {
  id: string;
  name: string;
  city: string;
  duration_days: number;
  price_total: number;
  rating: number;
  photo_url: string;
  description: string;
  includes: string[];
  tags: string[];
  match_score: number;
  ai_reason: string;
}

export interface SearchResponse {
  session_id: string;
  parsed: ParsedQuery;
  filters: SearchFilters;
  hotels: HotelResult[];
  tours: TourResult[];
  web_insight: string | null;
}

export interface SessionResponse extends SearchResponse {
  query: string;
}

export interface HotelDetail extends Omit<HotelResult, "match_score" | "ai_reason" | "total_price"> {}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err.detail;
    const message =
      typeof detail === "object" && detail?.message
        ? detail.message
        : typeof detail === "string"
          ? detail
          : res.statusText;
    throw new Error(message);
  }
  return res.json();
}

export async function searchHotels(query: string): Promise<SearchResponse> {
  return request<SearchResponse>("/api/search", {
    method: "POST",
    body: JSON.stringify({ query, init_data: getInitData() || undefined, use_web: true }),
  });
}

export async function loadSession(sessionId: string): Promise<SessionResponse> {
  return request<SessionResponse>(`/api/sessions/${sessionId}`);
}

export async function getHotel(id: string): Promise<HotelDetail> {
  return request<HotelDetail>(`/api/hotels/${id}`);
}

export async function bookHotel(id: string): Promise<{ status: string; message: string; booking_url?: string }> {
  return request(`/api/book/${id}`, {
    method: "POST",
    body: JSON.stringify({ init_data: getInitData() || undefined }),
  });
}
