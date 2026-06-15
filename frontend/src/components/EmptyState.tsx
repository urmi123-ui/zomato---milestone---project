import { Icon } from "./Icon";

interface EmptyStateProps {
  message?: string;
  onAdjust: () => void;
}

export function EmptyState({
  message = "No restaurants matched your filters.",
  onAdjust,
}: EmptyStateProps) {
  return (
    <section className="mx-auto max-w-3xl px-margin-mobile py-8 md:px-margin-desktop">
      <div className="flex flex-col items-center rounded-xl border border-surface-container-highest bg-surface-container-lowest p-8 text-center shadow-sm">
        <div className="mb-6 flex h-48 w-48 items-center justify-center rounded-full bg-surface-container">
          <Icon name="restaurant_menu" className="text-6xl text-outline" />
        </div>
        <h2 className="mb-2 text-2xl font-bold text-on-surface">{message}</h2>
        <p className="mb-8 max-w-md text-on-surface-variant">
          Try a broader area, different cuisine, or lower minimum rating.
        </p>
        <button
          type="button"
          onClick={onAdjust}
          className="rounded-full bg-primary px-6 py-3 text-xs font-semibold uppercase tracking-wide text-on-primary shadow-sm transition-colors hover:bg-primary-container"
        >
          Adjust preferences
        </button>
      </div>
    </section>
  );
}
