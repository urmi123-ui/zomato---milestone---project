import type { Recommendation, RecommendationResponse } from "../types";
import { AISummary } from "./AISummary";
import { FallbackBanner } from "./FallbackBanner";
import { RecommendationCard } from "./RecommendationCard";
import { RequestDetails } from "./RequestDetails";
import { Icon } from "./Icon";

interface ResultsSectionProps {
  response: RecommendationResponse;
  recommendations: Recommendation[];
}

export function ResultsSection({ response, recommendations }: ResultsSectionProps) {
  const [featured, ...rest] = recommendations;

  return (
    <section className="mx-auto max-w-[1280px] px-margin-mobile pb-16 pt-8 md:px-margin-desktop md:pb-24">
      {response.meta.llm_fallback && <FallbackBanner />}

      {response.summary && <AISummary summary={response.summary} />}

      <div className="mb-4 flex items-end justify-between">
        <h2 className="text-2xl font-bold text-on-surface">
          Top {recommendations.length} recommendations
        </h2>
        <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-on-surface-variant">
          <Icon name="sort" className="text-base" />
          Sorted by AI Match
        </div>
      </div>

      {featured && (
        <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-12">
          <RecommendationCard recommendation={featured} featured imageIndex={0} />
          {rest.length > 0 && (
            <div className="flex flex-col gap-6 lg:col-span-4">
              {rest.slice(0, 2).map((entry, index) => (
                <RecommendationCard
                  key={entry.restaurant.id}
                  recommendation={entry}
                  imageIndex={index + 1}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {rest.length > 2 && (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {rest.slice(2).map((entry, index) => (
            <RecommendationCard
              key={entry.restaurant.id}
              recommendation={entry}
              imageIndex={index + 3}
            />
          ))}
        </div>
      )}

      <RequestDetails meta={response.meta} />
    </section>
  );
}
