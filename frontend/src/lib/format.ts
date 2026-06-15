import type { Budget } from "../types";

export function formatCost(estimatedCost: number | null): string {
  if (estimatedCost == null) {
    return "N/A";
  }
  return `₹${Math.round(estimatedCost).toLocaleString("en-IN")} for two`;
}

export function formatLocation(location: string): string {
  return location.replace(/,\s*/g, " · ").replace(/\b\w/g, (ch) => ch.toUpperCase());
}

export function formatCuisines(cuisines: string[]): string {
  if (!cuisines.length) {
    return "N/A";
  }
  return cuisines.map((c) => c.replace(/\b\w/g, (ch) => ch.toUpperCase())).join(", ");
}

export function budgetLabel(budget: Budget): string {
  return {
    low: "Low (≤ ₹500)",
    medium: "Medium (≤ ₹1500)",
    high: "High (> ₹1500)",
  }[budget];
}

export function budgetChip(budget: Budget | null): string {
  if (!budget) {
    return "Unknown budget";
  }
  return `${budget.charAt(0).toUpperCase()}${budget.slice(1)} Budget`;
}

export const CARD_IMAGES = [
  "https://lh3.googleusercontent.com/aida-public/AB6AXuCrq0MnopqeSPh2zbWiuoIjkg2aZBQ9UVS_PjbD7bhSFUwUYRvTv3tT7J17ns8UsUr4JefMCkyVyww_HrWt22WhrUUKIRLGRSrtfzqTdzGu64qrzae_Otyev46f4zCDututI6NHpUwFL8iR14ZAGPlEkOQsB5oOlnXmyCwaTSI0sCjHpRRt4e6_HyEBAq0kdOu69mtHt57T6GJb9BbavackZK96UNkmfnZ0Xkwe7-JF-mxdl20Lleo8CgQY4EhIwBEjPZsKRcJgX4e5",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuAdJEiMPV3ZsXpij6vkgKgpZP46rf606nPTT7O8hzm0U1mws-SF1OR331AL6_QJ0khCwmzgVWMwz80cAzzj97L9czxVRrE2BJvEpGR22CVQMfp-q8Ubzez5md_7oE2FbKefqI4b2oqHs7-iLlj2hoO9RxIsBEwu-T8GmFSJJFGtTUplSaCE_a4nuQTJniaGC7AoU2GzRwk7jJTDFTNYNvveYEFXP1W1aUV9q4wMdZk8Y7fakBmmErvAEZV2dilxOFyhLryuM04GjAIu",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuA1ictfabYobwL8bKrUfhusVG56CmoxH2sWaJ_CqNnyVRoyTVB68ADDuVVvU74e5bPkxw1qieQSxw26FegECdmWUWrisSs75JASU5u09x-FdqSpbJjuNf8mYZigWAcyYCNK2ZzQQjkaAom_Ftzukn6igAUmGfLeov9sBS72HXhbzasaoqTak-64jJSGoGrmYQ1C_vFPP0oQMiduo5yFyW8fFDpEWnRFbc2fqzEQ3g7pWKYxBPT43KBNyRJNLUmBxWQB_5sDMDIYIBsy",
];

export function cardImage(index: number): string {
  return CARD_IMAGES[index % CARD_IMAGES.length];
}
