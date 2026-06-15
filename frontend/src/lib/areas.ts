export const CUSTOM_AREA_OPTION = "Other (type custom area)";

export const BANGALORE_AREA_OPTIONS: Record<string, string> = {
  "HSR Layout": "HSR",
  Indiranagar: "Indiranagar",
  Koramangala: "Koramangala",
  Whitefield: "Whitefield",
  Jayanagar: "Jayanagar",
  Marathahalli: "Marathahalli",
  Banashankari: "Banashankari",
  Bellandur: "Bellandur",
  "Electronic City": "Electronic City",
  BTM: "BTM",
  Domlur: "Domlur",
  Hebbal: "Hebbal",
  "JP Nagar": "JP Nagar",
  "MG Road": "MG Road",
  "Richmond Road": "Richmond Road",
};

export function buildAreaOptions(datasetAreas: string[]): string[] {
  const labels = Object.keys(BANGALORE_AREA_OPTIONS);
  const knownValues = new Set(
    Object.values(BANGALORE_AREA_OPTIONS).map((value) => value.toLowerCase()),
  );
  const extras = [...new Set(datasetAreas.map((area) => area.trim()).filter(Boolean))]
    .filter((area) => !knownValues.has(area.toLowerCase()))
    .sort()
    .slice(0, 30);
  return [...labels, ...extras, CUSTOM_AREA_OPTION];
}

export function resolveAreaSelection(pick: string, customArea: string): string {
  if (pick === CUSTOM_AREA_OPTION) {
    return customArea.trim();
  }
  if (pick in BANGALORE_AREA_OPTIONS) {
    return BANGALORE_AREA_OPTIONS[pick];
  }
  return pick.trim();
}

export const POPULAR_CUISINES = [
  "North Indian",
  "South Indian",
  "Chinese",
  "Italian",
  "Mughlai",
  "Fast Food",
  "Cafe",
  "Biryani",
  "Continental",
  "Thai",
];

export function orderCuisines(available: string[]): string[] {
  const normalized = new Set(available.map((c) => c.toLowerCase()));
  const ordered = POPULAR_CUISINES.filter(
    (cuisine) =>
      normalized.has(cuisine.toLowerCase()) ||
      [...normalized].some((item) => item.includes(cuisine.toLowerCase())),
  );
  const extras = available
    .filter((c) => !ordered.some((o) => o.toLowerCase() === c.toLowerCase()))
    .map((c) => c.replace(/\b\w/g, (ch) => ch.toUpperCase()))
    .sort()
    .slice(0, 20);
  return [...ordered, ...extras];
}
