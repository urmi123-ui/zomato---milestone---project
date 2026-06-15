from __future__ import annotations

CUSTOM_AREA_OPTION = "Other (type custom area)"

# Display label → filter value (substring matched against restaurant.location).
BANGALORE_AREA_OPTIONS: dict[str, str] = {
    "HSR Layout": "HSR",
    "Indiranagar": "Indiranagar",
    "Koramangala": "Koramangala",
    "Whitefield": "Whitefield",
    "Jayanagar": "Jayanagar",
    "Marathahalli": "Marathahalli",
    "Banashankari": "Banashankari",
    "Bellandur": "Bellandur",
    "Electronic City": "Electronic City",
    "BTM": "BTM",
    "Domlur": "Domlur",
    "Hebbal": "Hebbal",
    "JP Nagar": "JP Nagar",
    "MG Road": "MG Road",
    "Richmond Road": "Richmond Road",
}


def build_area_dropdown_options(dataset_areas: list[str]) -> list[str]:
    labels = list(BANGALORE_AREA_OPTIONS.keys())
    known_values = {value.lower() for value in BANGALORE_AREA_OPTIONS.values()}
    extras = sorted(
        {
            area.strip()
            for area in dataset_areas
            if area.strip() and area.strip().lower() not in known_values
        }
    )[:30]
    return labels + extras + [CUSTOM_AREA_OPTION]


def resolve_area_selection(pick: str, custom_area: str) -> str:
    if pick == CUSTOM_AREA_OPTION:
        return custom_area.strip()
    if pick in BANGALORE_AREA_OPTIONS:
        return BANGALORE_AREA_OPTIONS[pick]
    return pick.strip()
