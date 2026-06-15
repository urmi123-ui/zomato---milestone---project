export function LoadingState() {
  return (
    <section className="mx-auto max-w-7xl space-y-8 px-margin-mobile py-8 md:px-margin-desktop">
      <div className="space-y-4 py-8 text-center">
        <div className="mb-6 flex justify-center">
          <div className="spinner" />
        </div>
        <h2 className="text-2xl font-bold text-on-surface">Finding the best restaurants for you…</h2>
        <p className="text-on-surface-variant">AI ranking may take a few seconds</p>
      </div>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {[0, 1, 2].map((index) => (
          <div
            key={index}
            className={`space-y-4 overflow-hidden rounded-xl bg-surface-container-lowest p-4 shadow-sm ${
              index === 2 ? "hidden lg:block" : ""
            }`}
          >
            <div className="pulse-skeleton h-48 w-full rounded-lg bg-surface-container-highest" />
            <div className="pulse-skeleton h-6 w-3/4 rounded bg-surface-container-highest" />
            <div className="pulse-skeleton h-4 w-1/2 rounded bg-surface-container-highest" />
            <div className="flex gap-2 pt-2">
              <div className="pulse-skeleton h-8 w-16 rounded-full bg-surface-container-highest" />
              <div className="pulse-skeleton h-8 w-16 rounded-full bg-surface-container-highest" />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
