import { Icon } from "./Icon";

export function FallbackBanner() {
  return (
    <div className="mx-auto mb-8 flex max-w-[1280px] items-center gap-3 rounded-lg bg-tertiary-fixed p-4 text-on-tertiary-fixed shadow-sm md:px-margin-desktop">
      <Icon name="info" className="text-tertiary" />
      <p className="text-sm">
        AI ranking was unavailable — showing top-rated matches from your filtered list.
      </p>
    </div>
  );
}
