import type { FormEvent } from "react";
import type { Budget, FormState } from "../types";
import { CUSTOM_AREA_OPTION } from "../lib/areas";
import { budgetLabel } from "../lib/format";
import { Icon } from "./Icon";

interface PreferenceFormProps {
  form: FormState;
  areaOptions: string[];
  cuisineOptions: string[];
  loading: boolean;
  validationError: string | null;
  onChange: (updates: Partial<FormState>) => void;
  onSubmit: () => void;
}

const BUDGETS: Budget[] = ["low", "medium", "high"];

export function PreferenceForm({
  form,
  areaOptions,
  cuisineOptions,
  loading,
  validationError,
  onChange,
  onSubmit,
}: PreferenceFormProps) {
  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <section
      id="discover"
      className="relative z-20 mx-auto -mt-8 mb-16 max-w-[1000px] px-margin-mobile md:mb-24 md:px-margin-desktop"
    >
      <div className="rounded-xl border border-surface-container bg-surface-container-lowest p-6 shadow-card md:p-8">
        <form className="space-y-8" onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
            <div className="space-y-6">
              <div>
                <label htmlFor="area" className="mb-2 block text-xl font-semibold text-on-surface">
                  Location (Area) in Bangalore
                </label>
                <div className="relative">
                  <Icon
                    name="search"
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant"
                  />
                  <select
                    id="area"
                    value={form.areaPick}
                    onChange={(event) => onChange({ areaPick: event.target.value })}
                    className="w-full appearance-none rounded-lg border border-outline-variant bg-surface-container-low py-3 pl-10 pr-10 text-base text-on-surface outline-none transition-colors focus:border-primary focus:ring-1 focus:ring-primary"
                  >
                    {areaOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                  <Icon
                    name="expand_more"
                    className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant"
                  />
                </div>
              </div>

              {form.areaPick === CUSTOM_AREA_OPTION && (
                <div>
                  <label htmlFor="custom-area" className="mb-2 block text-sm font-semibold text-on-surface">
                    Custom area
                  </label>
                  <input
                    id="custom-area"
                    value={form.customArea}
                    onChange={(event) => onChange({ customArea: event.target.value })}
                    placeholder="e.g. Frazer Town, Sarjapur Road"
                    className="w-full rounded-lg border border-outline-variant bg-surface-container-low px-4 py-3 text-base outline-none transition-colors focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                </div>
              )}

              <div>
                <span className="mb-2 block text-xl font-semibold text-on-surface">Budget</span>
                <div className="flex rounded-lg border border-outline-variant bg-surface-container-low p-1">
                  {BUDGETS.map((budget) => (
                    <label key={budget} className="flex-1 text-center">
                      <input
                        type="radio"
                        name="budget"
                        value={budget}
                        checked={form.budget === budget}
                        onChange={() => onChange({ budget })}
                        className="sr-only"
                      />
                      <div
                        className={`cursor-pointer rounded-md py-2 text-sm transition-all ${
                          form.budget === budget
                            ? "bg-surface-container-lowest font-semibold text-primary shadow-sm"
                            : "text-on-surface-variant"
                        }`}
                      >
                        {budget === "low" ? "₹" : budget === "medium" ? "₹₹" : "₹₹₹"}
                      </div>
                    </label>
                  ))}
                </div>
                <p className="mt-2 text-sm text-on-surface-variant">{budgetLabel(form.budget)}</p>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <span className="mb-2 block text-xl font-semibold text-on-surface">Cuisine</span>
                <div className="mb-3 flex gap-4">
                  {(["pick", "custom"] as const).map((mode) => (
                    <label key={mode} className="flex items-center gap-2 text-sm">
                      <input
                        type="radio"
                        checked={form.cuisineMode === mode}
                        onChange={() => onChange({ cuisineMode: mode })}
                      />
                      {mode === "pick" ? "Pick a cuisine" : "Custom"}
                    </label>
                  ))}
                </div>
                {form.cuisineMode === "pick" ? (
                  <div className="relative">
                    <Icon
                      name="restaurant"
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant"
                    />
                    <select
                      value={form.cuisinePick}
                      onChange={(event) => onChange({ cuisinePick: event.target.value })}
                      className="w-full appearance-none rounded-lg border border-outline-variant bg-surface-container-low py-3 pl-10 pr-10 text-base outline-none transition-colors focus:border-primary focus:ring-1 focus:ring-primary"
                    >
                      {cuisineOptions.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                    <Icon
                      name="expand_more"
                      className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant"
                    />
                  </div>
                ) : (
                  <input
                    value={form.cuisineCustom}
                    onChange={(event) => onChange({ cuisineCustom: event.target.value })}
                    placeholder="e.g. North Indian"
                    className="w-full rounded-lg border border-outline-variant bg-surface-container-low px-4 py-3 text-base outline-none transition-colors focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                )}
              </div>

              <div>
                <div className="mb-2 flex items-end justify-between">
                  <label htmlFor="rating" className="text-xl font-semibold text-on-surface">
                    Minimum Rating
                  </label>
                  <div className="flex items-center gap-1 text-sm font-bold text-secondary-container">
                    <span>{form.minRating.toFixed(1)}</span>
                    <Icon name="star" filled className="text-base" />
                  </div>
                </div>
                <input
                  id="rating"
                  type="range"
                  min={0}
                  max={5}
                  step={0.5}
                  value={form.minRating}
                  onChange={(event) => onChange({ minRating: Number(event.target.value) })}
                  className="w-full appearance-none bg-transparent"
                />
                <div className="mt-1 flex justify-between px-1 text-[10px] font-semibold uppercase tracking-wide text-on-surface-variant">
                  <span>0.0</span>
                  <span>2.5</span>
                  <span>5.0</span>
                </div>
              </div>

              <div>
                <label htmlFor="top-k" className="mb-2 block text-sm font-semibold text-on-surface">
                  Number of recommendations
                </label>
                <input
                  id="top-k"
                  type="number"
                  min={1}
                  max={20}
                  value={form.topK}
                  onChange={(event) => onChange({ topK: Number(event.target.value) })}
                  className="w-full rounded-lg border border-outline-variant bg-surface-container-low px-4 py-3 text-base outline-none transition-colors focus:border-primary focus:ring-1 focus:ring-primary"
                />
              </div>
            </div>
          </div>

          <div>
            <label
              htmlFor="preferences"
              className="mb-2 flex items-center gap-2 text-xl font-semibold text-on-surface"
            >
              Additional Preferences
              <span className="rounded-sm bg-tertiary-fixed px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-on-tertiary-fixed">
                AI Powered
              </span>
            </label>
            <textarea
              id="preferences"
              rows={3}
              value={form.additionalPreferences}
              onChange={(event) => onChange({ additionalPreferences: event.target.value })}
              placeholder="e.g. family-friendly, quick service, outdoor seating"
              className="w-full resize-none rounded-lg border border-outline-variant bg-surface-container-low p-4 text-base outline-none transition-colors focus:border-primary focus:ring-1 focus:ring-primary"
            />
            <p className="mt-3 flex items-start gap-2 text-sm text-on-surface-variant">
              <Icon name="info" className="mt-0.5 text-lg" />
              Hard filters: area, budget, cuisine, and rating. Extra notes help AI personalize
              ranking and explanations.
            </p>
          </div>

          {validationError && (
            <div className="rounded-lg border border-error/20 bg-error-container px-4 py-3 text-sm text-on-error-container">
              {validationError}
            </div>
          )}

          <div className="flex justify-end border-t border-surface-container-highest pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-full bg-primary px-8 py-4 text-lg font-semibold text-on-primary shadow-cta transition-all hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgba(226,55,68,0.4)] disabled:cursor-not-allowed disabled:opacity-60 md:w-auto"
            >
              <Icon name="auto_awesome" />
              {loading ? "Finding restaurants…" : "Get Recommendations"}
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}
