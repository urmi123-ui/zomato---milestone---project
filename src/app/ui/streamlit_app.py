from __future__ import annotations

import sys
from pathlib import Path

# Streamlit adds this file's directory to sys.path, which breaks `import app`
# if this file were named app.py. Ensure `src/` is on the path first.
_SRC_ROOT = Path(__file__).resolve().parents[2]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import streamlit as st

from app.deploy.bootstrap import DatasetBootstrapError, ensure_dataset
from app.deploy.env import apply_streamlit_secrets

apply_streamlit_secrets()

from app.config import clear_settings_cache, get_settings
from app.data.dedup import deduplicate_recommendations_by_name
from app.models.preferences import UserPreferences
from app.models.recommendation import RecommendationResponse
from app.services.orchestrator import RecommendationOrchestrator, StoreNotLoadedError
from app.ui.areas import (
    CUSTOM_AREA_OPTION,
    build_area_dropdown_options,
    resolve_area_selection,
)
from app.ui.components import format_cost, format_cuisines, parse_preferences_safe, validate_form_inputs


@st.cache_resource
def get_orchestrator() -> RecommendationOrchestrator:
    return RecommendationOrchestrator()


@st.cache_data(show_spinner=False)
def load_area_suggestions() -> list[str]:
    orchestrator = get_orchestrator()
    try:
        orchestrator.repository.load()
        return orchestrator.repository.distinct_areas()
    except Exception:
        return []


@st.cache_data(show_spinner=False)
def load_cuisine_suggestions() -> list[str]:
    orchestrator = get_orchestrator()
    try:
        orchestrator.repository.load()
        popular = [
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
        ]
        available = set(orchestrator.repository.distinct_cuisines())
        ordered = [
            cuisine
            for cuisine in popular
            if cuisine.lower() in available or any(cuisine.lower() in c for c in available)
        ]
        extras = sorted(c.title() for c in available if c not in {x.lower() for x in ordered})[:30]
        return ordered + extras[:20]
    except Exception:
        return ["North Indian", "Chinese", "Italian", "Mughlai"]


def _init_session_state() -> None:
    defaults = {
        "last_response": None,
        "last_error": None,
        "form_defaults": {
            "location_pick": "Koramangala",
            "location_custom": "",
            "budget": "medium",
            "cuisine_mode": "Pick a cuisine",
            "cuisine_custom": "North Indian",
            "cuisine_pick": "North Indian",
            "min_rating": 3.5,
            "additional_preferences": "",
            "top_k": 5,
        },
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _resolve_cuisine(mode: str, pick: str, custom: str) -> str:
    if mode == "Enter custom cuisine":
        return custom
    return pick


def render_preference_form() -> UserPreferences | None:
    st.subheader("Your preferences")
    st.caption("Hard filters: area in Bangalore, budget, cuisine, and rating. Extra notes are used by Groq for ranking.")

    area_options = build_area_dropdown_options(load_area_suggestions())
    cuisines = load_cuisine_suggestions()
    defaults = st.session_state.form_defaults

    with st.form("preferences_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            default_pick = defaults["location_pick"]
            if default_pick not in area_options:
                default_pick = "Koramangala" if "Koramangala" in area_options else area_options[0]

            location_pick = st.selectbox(
                "Location (Area) in Bangalore",
                options=area_options,
                index=area_options.index(default_pick),
            )
            if location_pick == CUSTOM_AREA_OPTION:
                location_custom = st.text_input(
                    "Custom area",
                    value=defaults["location_custom"],
                    placeholder="e.g. Frazer Town, Sarjapur Road",
                )
            else:
                location_custom = defaults["location_custom"]

            budget = st.selectbox(
                "Budget (for two)",
                options=["low", "medium", "high"],
                index=["low", "medium", "high"].index(defaults["budget"]),
                format_func=lambda value: {"low": "Low (≤ ₹500)", "medium": "Medium (≤ ₹1500)", "high": "High (> ₹1500)"}[value],
            )

        with col2:
            cuisine_mode = st.radio(
                "Cuisine",
                options=["Pick a cuisine", "Enter custom cuisine"],
                horizontal=True,
                index=0 if defaults["cuisine_mode"] == "Pick a cuisine" else 1,
            )
            if cuisine_mode == "Pick a cuisine":
                cuisine_pick = st.selectbox(
                    "Cuisine type",
                    options=cuisines or ["North Indian"],
                    index=(cuisines or ["North Indian"]).index(defaults["cuisine_pick"])
                    if defaults["cuisine_pick"] in (cuisines or ["North Indian"])
                    else 0,
                    label_visibility="collapsed",
                )
                cuisine_custom = defaults["cuisine_custom"]
            else:
                cuisine_pick = defaults["cuisine_pick"]
                cuisine_custom = st.text_input(
                    "Custom cuisine",
                    value=defaults["cuisine_custom"],
                    placeholder="e.g. North Indian",
                    label_visibility="collapsed",
                )

            min_rating = st.slider("Minimum rating", min_value=0.0, max_value=5.0, value=float(defaults["min_rating"]), step=0.5)
            top_k = st.number_input("Number of recommendations", min_value=1, max_value=20, value=int(defaults["top_k"]))

        additional_preferences = st.text_area(
            "Additional preferences (optional)",
            value=defaults["additional_preferences"],
            placeholder="e.g. family-friendly, quick service, outdoor seating",
            help="Not used as a hard filter — Groq uses this when ranking and explaining results.",
        )

        submitted = st.form_submit_button("Get recommendations", type="primary", use_container_width=True)

    if not submitted:
        return None

    location = resolve_area_selection(location_pick, location_custom)
    cuisine = _resolve_cuisine(cuisine_mode, cuisine_pick, cuisine_custom)

    st.session_state.form_defaults = {
        "location_pick": location_pick,
        "location_custom": location_custom,
        "budget": budget,
        "cuisine_mode": cuisine_mode,
        "cuisine_custom": cuisine_custom,
        "cuisine_pick": cuisine_pick,
        "min_rating": min_rating,
        "additional_preferences": additional_preferences,
        "top_k": top_k,
    }

    validation_error = validate_form_inputs(location, cuisine)
    if validation_error:
        st.error(validation_error)
        return None

    preferences, error = parse_preferences_safe(
        location=location,
        budget=budget,
        cuisine=cuisine,
        min_rating=min_rating,
        additional_preferences=additional_preferences or None,
        top_k=int(top_k),
    )
    if error:
        st.error(error)
        return None
    return preferences


def render_results(response: RecommendationResponse) -> None:
    meta = response.meta or {}
    status = meta.get("status")

    if status == "empty":
        st.warning(meta.get("message", "No restaurants matched your filters."))
        st.info("Try a broader location, a different cuisine, or a lower minimum rating.")
        return

    if meta.get("llm_fallback"):
        st.info(
            "Groq ranking was unavailable — showing top-rated matches from your filtered list. "
            "Check your API key or network if this persists."
        )

    if response.summary:
        st.subheader("Summary")
        st.write(response.summary)

    recommendations = deduplicate_recommendations_by_name(response.recommendations)
    if not recommendations:
        st.warning("No recommendations to display.")
        return

    st.subheader(f"Top {len(recommendations)} recommendations")

    for rec in recommendations:
        restaurant = rec.restaurant
        with st.container(border=True):
            header_left, header_right = st.columns([3, 1])
            with header_left:
                st.markdown(f"### #{rec.rank} {restaurant.name}")
                st.caption(restaurant.location.replace(", ", " · ").title())
            with header_right:
                st.metric("Rating", f"{restaurant.rating:.1f} ★")

            detail1, detail2, detail3 = st.columns(3)
            with detail1:
                st.write(f"**Cuisine:** {format_cuisines(restaurant.cuisines)}")
            with detail2:
                st.write(f"**Cost:** {format_cost(restaurant.estimated_cost)}")
            with detail3:
                band = restaurant.budget_band or "unknown"
                st.write(f"**Budget band:** {band}")

            st.markdown(f"**Why this pick:** {rec.explanation}")

    with st.expander("Request details"):
        st.json(
            {
                "status": status,
                "candidates_considered": meta.get("candidates_considered"),
                "candidates_sent_to_llm": meta.get("candidates_sent_to_llm"),
                "llm_latency_ms": meta.get("llm_latency_ms"),
                "filter_ms": meta.get("filter_ms"),
                "llm_model": meta.get("llm_model"),
                "correlation_id": meta.get("correlation_id"),
            }
        )


def main() -> None:
    st.set_page_config(
        page_title="Zomato AI Recommendations",
        page_icon="🍽️",
        layout="wide",
    )

    _init_session_state()

    st.title("🍽️ AI Restaurant Recommendations")
    st.write(
        "Personalized restaurant suggestions powered by structured Zomato data and Groq LLM explanations."
    )

    try:
        if not get_settings().data_path.is_file():
            with st.spinner("Preparing restaurant dataset (first run may take a minute)…"):
                clear_settings_cache()
                ensure_dataset()
                get_orchestrator.clear()
        orchestrator = get_orchestrator()
        orchestrator.repository.load()
    except DatasetBootstrapError as exc:
        st.error(str(exc))
        st.stop()
    except StoreNotLoadedError:
        st.error(
            "Restaurant dataset is not loaded. Run ingestion first:\n\n"
            "`python -m app.ingestion.pipeline` or `python scripts/bootstrap_data.py`"
        )
        st.stop()

    preferences = render_preference_form()

    if preferences is not None:
        with st.spinner("Finding the best restaurants for you… (Groq may take a few seconds)"):
            try:
                response = get_orchestrator().execute(preferences)
                st.session_state.last_response = response
                st.session_state.last_error = None
            except StoreNotLoadedError as exc:
                st.session_state.last_error = str(exc)
                st.error(f"Dataset error: {exc}")
            except Exception as exc:
                st.session_state.last_error = str(exc)
                st.error(f"Something went wrong: {exc}")

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    if st.session_state.last_response is not None:
        render_results(st.session_state.last_response)


if __name__ == "__main__":
    main()
