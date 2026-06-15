interface IconProps {
  name: string;
  filled?: boolean;
  className?: string;
}

export function Icon({ name, filled = false, className = "" }: IconProps) {
  return (
    <span className={`material-symbols-outlined ${filled ? "fill" : ""} ${className}`.trim()}>
      {name}
    </span>
  );
}
