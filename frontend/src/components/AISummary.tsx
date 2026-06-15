import { Icon } from "./Icon";

interface AISummaryProps {
  summary: string;
}

export function AISummary({ summary }: AISummaryProps) {
  return (
    <section className="mb-6">
      <div className="relative overflow-hidden rounded-xl border border-tertiary-fixed-dim bg-tertiary-fixed p-4 shadow-sm md:p-5">
        <div className="ai-shimmer pointer-events-none absolute inset-0 opacity-40" />
        <div className="relative z-10 flex items-start gap-4">
          <div className="flex-shrink-0 rounded-full bg-tertiary p-2 text-on-tertiary">
            <Icon name="auto_awesome" filled />
          </div>
          <div>
            <h2 className="mb-1 text-xl font-semibold text-on-tertiary-fixed">AI Insights</h2>
            <p className="text-sm leading-5 text-on-tertiary-fixed">{summary}</p>
          </div>
        </div>
      </div>
    </section>
  );
}
