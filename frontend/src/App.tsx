import { useEffect, useMemo, useState } from "react";
import type { AppStatus, FormState, RecommendationResponse } from "./types";
import {
  buildAreaOptions,
  orderCuisines,
  resolveAreaSelection,
} from "./lib/areas";
import {
  deduplicateRecommendations,
  fetchAreas,
  fetchCuisines,
  fetchRecommendations,
} from "./api/client";
import { BottomNav, Header } from "./components/Layout";
import { Hero } from "./components/Hero";
import { PreferenceForm } from "./components/PreferenceForm";
import { LoadingState } from "./components/LoadingState";
import { EmptyState } from "./components/EmptyState";
import { ResultsSection } from "./components/ResultsSection";

const DEFAULT_FORM: FormState = {
  areaPick: "Koramangala",
  customArea: "",
  budget: "medium",
  cuisineMode: "pick",
  cuisinePick: "North Indian",
  cuisineCustom: "",
  minRating: 3.5,
  topK: 5,
  additionalPreferences: "",
};

export default function App() {
  const [form, setForm] = useState<FormState>(DEFAULT_FORM);
  const [areaOptions, setAreaOptions] = useState<string[]>(buildAreaOptions([]));
  const [cuisineOptions, setCuisineOptions] = useState<string[]>(["North Indian"]);
  const [status, setStatus] = useState<AppStatus>("idle");
  const [validationError, setValidationError] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [response, setResponse] = useState<RecommendationResponse | null>(null);

  useEffect(() => {
    async function loadMetadata() {
      try {
        const [areas, cuisines] = await Promise.all([fetchAreas(), fetchCuisines()]);
        const nextAreas = buildAreaOptions(areas);
        setAreaOptions(nextAreas);
        setCuisineOptions(orderCuisines(cuisines));
        setForm((current) => ({
          ...current,
          areaPick: nextAreas.includes(current.areaPick) ? current.areaPick : "Koramangala",
          cuisinePick: orderCuisines(cuisines).includes(current.cuisinePick)
            ? current.cuisinePick
            : orderCuisines(cuisines)[0] ?? "North Indian",
        }));
      } catch {
        setAreaOptions(buildAreaOptions([]));
      }
    }
    void loadMetadata();
  }, []);

  const recommendations = useMemo(
    () => (response ? deduplicateRecommendations(response.recommendations) : []),
    [response],
  );

  const updateForm = (updates: Partial<FormState>) => {
    setForm((current) => ({ ...current, ...updates }));
    setValidationError(null);
  };

  const scrollToForm = () => {
    document.getElementById("discover")?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = async () => {
    const location = resolveAreaSelection(form.areaPick, form.customArea);
    const cuisine = form.cuisineMode === "custom" ? form.cuisineCustom.trim() : form.cuisinePick;

    if (!location) {
      setValidationError("Location is required.");
      return;
    }
    if (!cuisine) {
      setValidationError("Cuisine is required.");
      return;
    }

    setValidationError(null);
    setErrorMessage(null);
    setStatus("loading");
    setResponse(null);

    try {
      const result = await fetchRecommendations({
        location,
        budget: form.budget,
        cuisine,
        min_rating: form.minRating,
        additional_preferences: form.additionalPreferences.trim() || null,
        top_k: form.topK,
      });

      setResponse(result);
      if (result.meta.status === "empty" || result.recommendations.length === 0) {
        setStatus("empty");
      } else {
        setStatus("success");
        window.setTimeout(() => {
          document.getElementById("results")?.scrollIntoView({ behavior: "smooth" });
        }, 100);
      }
    } catch (error) {
      setStatus("error");
      setErrorMessage(error instanceof Error ? error.message : "Something went wrong.");
    }
  };

  return (
    <div className="relative min-h-screen pb-24 md:pb-0">
      <Header />
      <main className="flex-grow pt-[72px]">
        <Hero />
        <PreferenceForm
          form={form}
          areaOptions={areaOptions}
          cuisineOptions={cuisineOptions}
          loading={status === "loading"}
          validationError={validationError}
          onChange={updateForm}
          onSubmit={() => void handleSubmit()}
        />

        {status === "loading" && <LoadingState />}

        {status === "error" && errorMessage && (
          <section className="mx-auto max-w-3xl px-margin-mobile pb-8 md:px-margin-desktop">
            <div className="rounded-lg border border-error/20 bg-error-container px-4 py-3 text-sm text-on-error-container">
              {errorMessage}
            </div>
          </section>
        )}

        {status === "empty" && (
          <EmptyState
            message={response?.meta.message ?? "No restaurants matched your filters."}
            onAdjust={scrollToForm}
          />
        )}

        {status === "success" && response && recommendations.length > 0 && (
          <div id="results">
            <ResultsSection response={response} recommendations={recommendations} />
          </div>
        )}
      </main>
      <BottomNav />
    </div>
  );
}
