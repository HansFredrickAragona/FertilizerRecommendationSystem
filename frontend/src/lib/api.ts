export type Fertilizer = {
  name: string;
  n: number;
  p: number;
  k: number;
};

export type Catalog = {
  crops: string[];
  fertilizers: Fertilizer[];
};

export type RecommendationRequest = {
  crop_label: string;
  n_status: string;
  p_status: string;
  k_status: string;
  soil_ph: number;
  raw_area: number;
  area_unit: string;
  selected_inventory_names?: string[];
};

export type MixEntry = {
  Source: string;
  Prescription: string[];
  "Total Weight": number;
  "Total Sacks": number;
  "Applied N": number;
  "Applied P": number;
  "Applied K": number;
};

export type PhResult = {
  ph_status: string;
  ph_action: string;
  borderline_warning: boolean;
  borderline_message: string | null;
  recommendation_message: string;
  soil_ph: number;
  perfect_ph: number;
};

export type RecommendationResponse = {
  selected_crop_label: string;
  selected_crop: string;
  area_ha: number;
  unit_label: string;
  raw_area: number;
  base_targets_per_ha: Record<string, number>;
  total_base: Record<string, number>;
  ph_result: PhResult;
  user_inventory: Fertilizer[];
  inventory_check: { valid: boolean; reason: string | null; details: unknown };
  inventory_sufficiency: {
    has_n: boolean;
    has_p: boolean;
    has_k: boolean;
    missing_nutrients: string[];
  };
  standard_mix: MixEntry[];
  farmer_selected_mix?: MixEntry[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchCatalog(): Promise<Catalog> {
  const res = await fetch(`${API_BASE}/catalog`);
  if (!res.ok) throw new Error(`Catalog request failed (${res.status})`);
  return res.json();
}

export async function fetchRecommendation(
  payload: RecommendationRequest,
): Promise<RecommendationResponse> {
  const res = await fetch(`${API_BASE}/recommendation`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(
      `Recommendation failed (${res.status}): ${detail.slice(0, 200)}`,
    );
  }
  return res.json();
}
