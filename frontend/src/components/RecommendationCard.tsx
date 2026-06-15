import type { Recommendation } from "../types";
import {
  budgetChip,
  cardImage,
  formatCost,
  formatLocation,
} from "../lib/format";
import { Icon } from "./Icon";

interface RecommendationCardProps {
  recommendation: Recommendation;
  featured?: boolean;
  imageIndex: number;
}

export function RecommendationCard({
  recommendation,
  featured = false,
  imageIndex,
}: RecommendationCardProps) {
  const { restaurant, explanation, rank } = recommendation;

  if (featured) {
    return (
      <article className="relative overflow-hidden rounded-card border-2 border-primary/20 bg-surface-container-lowest card-shadow featured-shadow md:col-span-12 lg:col-span-8">
        <div className="absolute left-4 top-4 z-10 flex items-center gap-1 rounded-md gold-foil px-3 py-1 text-xs font-bold shadow-md">
          <Icon name="stars" filled className="text-sm" />
          Top Pick
        </div>
        <div className="flex h-full flex-col md:flex-row">
          <div className="relative h-48 w-full md:h-auto md:w-2/5">
            <img
              src={cardImage(imageIndex)}
              alt={restaurant.name}
              className="h-full w-full object-cover"
            />
          </div>
          <div className="flex w-full flex-col justify-between p-4 md:w-3/5 md:p-6">
            <div>
              <div className="mb-1 flex items-start justify-between">
                <h3 className="text-2xl font-bold leading-tight text-on-surface">{restaurant.name}</h3>
                <div className="ml-2 flex shrink-0 items-center gap-1 rounded bg-secondary-container px-2 py-1 shadow-sm">
                  <span className="text-xs font-bold">{restaurant.rating.toFixed(1)}</span>
                  <Icon name="star" filled className="text-xs" />
                </div>
              </div>
              <p className="mb-3 flex items-center gap-1 text-sm text-on-surface-variant">
                <Icon name="location_on" className="text-base" />
                {formatLocation(restaurant.location)}
                <span className="mx-1 text-outline-variant">•</span>
                {formatCost(restaurant.estimated_cost)}
              </p>
              <div className="mb-4 flex flex-wrap gap-2">
                {restaurant.cuisines.slice(0, 3).map((cuisine) => (
                  <span
                    key={cuisine}
                    className="rounded bg-[#F0F0F0] px-2 py-1 text-xs font-semibold uppercase tracking-wide text-on-surface"
                  >
                    {cuisine}
                  </span>
                ))}
                <span className="rounded bg-[#F0F0F0] px-2 py-1 text-xs font-semibold uppercase tracking-wide text-on-surface">
                  {budgetChip(restaurant.budget_band)}
                </span>
              </div>
            </div>
            <div className="relative mt-4 rounded-r-md border-l-4 border-tertiary bg-[#EBF2FF] p-3">
              <Icon name="psychology" className="absolute right-2 top-2 text-3xl text-tertiary/20" />
              <p className="relative z-10 text-sm italic text-on-surface">&ldquo;{explanation}&rdquo;</p>
            </div>
          </div>
        </div>
      </article>
    );
  }

  return (
    <article className="flex h-full flex-col overflow-hidden rounded-card border border-outline-variant/30 bg-surface-container-lowest card-shadow">
      <div className="relative h-32">
        <div className="absolute left-2 top-2 z-10 rounded border border-outline-variant/20 bg-surface/90 px-2 py-0.5 text-xs font-semibold shadow-sm backdrop-blur-sm">
          #{rank}
        </div>
        <img src={cardImage(imageIndex)} alt={restaurant.name} className="h-full w-full object-cover" />
      </div>
      <div className="flex flex-grow flex-col p-4 md:p-5">
        <div className="mb-1 flex items-start justify-between">
          <h3 className="text-xl font-semibold text-on-surface">{restaurant.name}</h3>
          <div className="flex items-center gap-0.5 rounded bg-secondary-container px-1.5 py-0.5 shadow-sm">
            <span className="text-xs font-bold">{restaurant.rating.toFixed(1)}</span>
            <Icon name="star" filled className="text-[10px]" />
          </div>
        </div>
        <p className="mb-2 text-sm text-on-surface-variant">
          {formatLocation(restaurant.location)} • {formatCost(restaurant.estimated_cost)}
        </p>
        <div className="mb-3 flex flex-wrap gap-1.5">
          {restaurant.cuisines.slice(0, 2).map((cuisine) => (
            <span
              key={cuisine}
              className="rounded bg-[#F0F0F0] px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-on-surface"
            >
              {cuisine}
            </span>
          ))}
        </div>
        <div className="mt-auto rounded-r border-l-2 border-tertiary bg-[#EBF2FF] p-2">
          <p className="text-xs leading-snug text-on-surface">&ldquo;{explanation}&rdquo;</p>
        </div>
      </div>
    </article>
  );
}
