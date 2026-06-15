import { Icon } from "./Icon";

export function Hero() {
  return (
    <section className="hero-bg relative overflow-hidden px-margin-mobile py-16 text-center md:px-margin-desktop md:py-24">
      <div className="relative z-10 mx-auto max-w-4xl">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-tertiary-fixed px-3 py-1 text-xs font-semibold uppercase tracking-wide text-on-tertiary-fixed shadow-sm">
          <Icon name="bolt" className="text-base" />
          Powered by Groq AI
        </div>
        <h2 className="mb-6 text-4xl font-extrabold leading-tight tracking-tight text-on-surface md:text-[56px] md:leading-[64px]">
          Discover <span className="text-primary">Bangalore&apos;s</span> Best
        </h2>
        <p className="mx-auto max-w-2xl text-base leading-6 text-on-surface-variant md:text-lg">
          Personalized restaurant picks powered by real data and advanced AI. Tell us what
          you&apos;re craving, and we&apos;ll handle the rest.
        </p>
      </div>
    </section>
  );
}
