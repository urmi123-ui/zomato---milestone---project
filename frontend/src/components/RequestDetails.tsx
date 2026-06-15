import { Icon } from "./Icon";

interface RequestDetailsProps {
  meta: Record<string, unknown>;
}

export function RequestDetails({ meta }: RequestDetailsProps) {
  return (
    <section className="mt-10 border-t border-outline-variant/30 pt-4">
      <details className="group">
        <summary className="flex cursor-pointer list-none items-center text-xs font-semibold uppercase tracking-wide text-on-surface-variant transition-colors hover:text-on-surface">
          <Icon name="chevron_right" className="mr-2 transition-transform group-open:rotate-90" />
          Request details (Debug/Meta)
        </summary>
        <div className="mt-4 overflow-x-auto rounded-md bg-surface-container-high p-4 font-mono text-xs text-on-surface-variant">
          <pre>{JSON.stringify(meta, null, 2)}</pre>
        </div>
      </details>
    </section>
  );
}
