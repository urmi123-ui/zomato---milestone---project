import { Icon } from "./Icon";

export function Header() {
  return (
    <header className="fixed top-0 left-0 z-50 flex w-full items-center justify-between bg-surface px-margin-mobile py-4 shadow-sm md:px-margin-desktop">
      <div className="flex items-center gap-3">
        <Icon name="restaurant" className="text-3xl text-primary" />
        <h1 className="text-2xl font-bold text-primary">DineAI</h1>
      </div>
      <div className="flex items-center gap-2 text-on-surface-variant md:gap-4">
        <button
          type="button"
          className="rounded-full p-2 transition-colors hover:bg-surface-container-high"
          aria-label="Location"
        >
          <Icon name="location_on" />
        </button>
        <button
          type="button"
          className="rounded-full p-2 transition-colors hover:bg-surface-container-high"
          aria-label="Account"
        >
          <Icon name="account_circle" />
        </button>
      </div>
    </header>
  );
}

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 z-50 flex w-full items-center justify-around rounded-t-xl border-t border-outline-variant bg-surface px-4 py-3 shadow-lg md:hidden">
      <a
        href="#discover"
        className="flex scale-110 flex-col items-center justify-center rounded-full bg-tertiary-container px-4 py-1 text-on-tertiary-container transition-transform"
      >
        <Icon name="explore" />
        <span className="mt-1 text-[10px] font-semibold uppercase tracking-wide">Discover</span>
      </a>
      {["bookmark", "history", "person"].map((item) => (
        <button
          key={item}
          type="button"
          className="flex flex-col items-center justify-center text-on-surface-variant transition-colors hover:text-primary"
        >
          <Icon name={item} />
          <span className="mt-1 text-[10px] font-semibold uppercase tracking-wide">
            {item === "bookmark" ? "Saved" : item === "history" ? "History" : "Profile"}
          </span>
        </button>
      ))}
    </nav>
  );
}
