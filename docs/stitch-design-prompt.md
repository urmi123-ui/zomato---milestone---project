# Google Stitch Design Prompt — Zomato AI Restaurant Recommendations

Use this document as a copy-paste brief for **Google Stitch** to generate frontend designs for this project.

---

## Project brief

Design a **modern, polished web UI** for an **AI-powered restaurant recommendation app** inspired by Zomato. The product helps users in **Bangalore** discover restaurants based on structured preferences, then shows **AI-ranked results with personalized explanations** powered by real Zomato dataset data + Groq LLM.

This is a **single-page web app** (not a mobile native app). The backend already exists (FastAPI + orchestrator). The current UI is a basic Streamlit form — we need a **production-quality frontend design** that feels like a real consumer food-discovery product.

**Design goal:** Make it feel trustworthy, appetizing, and smart — like Zomato meets a premium AI assistant. Avoid generic "AI SaaS dashboard" aesthetics.

---

## Product flow

```
User fills preference form → Submit → Loading (2–15s) → AI Summary (optional) → Ranked restaurant cards
```

**User journey:**

1. Land on hero + preference form
2. Select area in Bangalore, budget, cuisine, min rating, optional notes
3. Tap **"Get recommendations"**
4. See loading state while AI ranks results
5. View summary paragraph + ranked cards with ratings, cost, cuisine, and "Why this pick" AI explanation
6. Handle empty results, errors, and fallback states gracefully

---

## Brand & visual direction

**Mood:** Warm, food-forward, confident, clean, mobile-first but desktop-polished

**Reference inspiration (do not copy):**

- Zomato (food discovery, ratings, locality)
- Swiggy Dineout (cards, ratings, cost)
- Modern AI products with clear explainability (not chat-heavy)

**Suggested palette:**

- Primary: Zomato-adjacent red/coral (`#E23744` or similar) for CTAs and accents
- Secondary: Deep charcoal/near-black for text (`#1C1C1C`)
- Background: Off-white / warm gray (`#FAFAFA`, `#F5F5F5`)
- Success/rating: Amber/gold for stars (`#FFB800`)
- Info banners: Soft blue for fallback/info states
- Warning/empty: Soft amber or muted orange

**Typography:**

- Headings: Bold, modern sans (e.g. Inter, Plus Jakarta Sans, or similar)
- Body: Highly readable sans, 14–16px base
- Use clear hierarchy: Hero H1 → Section H2 → Card title H3

**Imagery:**

- Use subtle food/restaurant placeholder imagery or abstract patterns in hero
- Restaurant cards can include optional thumbnail placeholders (we don't have real photos in MVP — use elegant placeholders)

**UI style:**

- Rounded corners (12–16px on cards)
- Soft shadows on cards
- Generous whitespace
- Chip/tag style for cuisine and budget band
- Star ratings visually prominent
- Rank badges (#1, #2, #3) with subtle emphasis on top pick

---

## Screens to design

Design **one main page** with these **sections/states** (can be separate artboards or variants):

### 1. Default / Form state (primary screen)

**Header**

- Logo/wordmark: **"Zomato AI Recommendations"** or shorter **"DineAI"** / **"PickRight"** (designer's choice, food + AI vibe)
- Tagline: *"Personalized restaurant picks for Bangalore, powered by real data and AI."*
- Optional small badge: "Powered by Groq AI"

**Preference form card** (centered, max-width ~960px, 2-column layout on desktop, stacked on mobile)

| Field | UI control | Details |
|-------|------------|---------|
| **Location (Area) in Bangalore** | Searchable dropdown | Pre-filled options: HSR Layout, Indiranagar, Koramangala, Whitefield, Jayanagar, Marathahalli, Banashankari, Bellandur, Electronic City, BTM, Domlur, Hebbal, JP Nagar, MG Road, Richmond Road + **"Other (type custom area)"** |
| **Custom area** | Text input (shown only when "Other" selected) | Placeholder: "e.g. Frazer Town, Sarjapur Road" |
| **Budget (for two)** | Segmented control or select | Low (≤ ₹500), Medium (≤ ₹1500), High (> ₹1500) |
| **Cuisine** | Toggle: "Pick a cuisine" / "Custom" + dropdown or text input | Options: North Indian, South Indian, Chinese, Italian, Mughlai, Fast Food, Cafe, Biryani, Continental, Thai |
| **Minimum rating** | Slider 0.0–5.0 (step 0.5) | Show current value + star preview |
| **Number of recommendations** | Stepper or number input | Default 5, range 1–20 |
| **Additional preferences** | Multiline text area (optional) | Placeholder: "family-friendly, quick service, outdoor seating" + helper text: *"Used by AI for ranking — not a hard filter"* |

**Primary CTA:** Full-width button — **"Get recommendations"**

**Microcopy under form:** *"Hard filters: area, budget, cuisine, and rating. Extra notes help AI personalize ranking and explanations."*

---

### 2. Loading state

After submit, replace/disable form CTA and show:

- Skeleton cards OR animated loader
- Message: **"Finding the best restaurants for you…"**
- Subtext: *"AI ranking may take a few seconds"*
- Progress indicator (spinner or subtle pulse)

---

### 3. Results state (success)

**AI Summary block** (optional, above cards)

- Soft highlighted panel with AI icon
- Example copy: *"Five strong North Indian options in Koramangala within a medium budget, with family-friendly picks prioritized."*

**Section title:** **"Top 5 recommendations"**

**Recommendation card** (repeat for each result — design 3–5 cards, #1 most prominent)

Each card includes:

- **Rank badge** (#1, #2, #3…)
- **Restaurant name** (bold, large)
- **Location/area** (caption, e.g. "Koramangala · Bangalore")
- **Rating** (large, e.g. 4.5 ★)
- **Cuisine tags** (chips)
- **Estimated cost** (e.g. "₹800 for two")
- **Budget band** chip (low / medium / high)
- **"Why this pick"** section — AI explanation in a distinct quote/callout box with subtle AI accent border
- Optional: "View on Zomato" link placeholder

**Card #1 treatment:** Slightly larger, "Top pick" ribbon, stronger shadow or accent border

**Collapsible footer:** "Request details" expander showing debug meta (candidates considered, LLM latency) — keep visually secondary/developer-ish

---

### 4. Empty state

When no restaurants match filters:

- Illustration or icon (empty plate / map pin)
- Title: **"No restaurants matched your filters"**
- Body: *"Try a broader area, different cuisine, or lower minimum rating."*
- Secondary CTA: **"Adjust preferences"**

---

### 5. Fallback banner (inline, above results)

Info banner (non-blocking):

- *"AI ranking was unavailable — showing top-rated matches from your filtered list."*
- Soft info styling, dismissible optional

---

### 6. Error states

- **Validation error:** Inline under form field (e.g. "Location is required")
- **System error:** Error toast/banner (e.g. "Something went wrong. Please try again.")
- **Dataset missing:** Full-width error panel with setup instructions

---

## Sample content for realistic mockups

Use this data in cards:

**User inputs (example):**

- Area: Koramangala
- Budget: Medium (≤ ₹1500)
- Cuisine: North Indian
- Min rating: 4.0
- Additional: "family-friendly, good for groups"
- Top K: 5

**Sample recommendations:**

| Rank | Name | Location | Rating | Cost | Cuisine | AI explanation |
|------|------|----------|--------|------|---------|----------------|
| 1 | Meghana Foods | Koramangala · Bangalore | 4.6 ★ | ₹800 for two | Biryani, Andhra | "Highly rated for authentic Andhra flavors in Koramangala, fits your medium budget, and works well for group dining." |
| 2 | Empire Restaurant | Koramangala 5th Block · Bangalore | 4.3 ★ | ₹600 for two | North Indian, Mughlai | "Reliable North Indian spot with strong ratings and affordable pricing for families." |
| 3 | The Fatty Bao | Koramangala · Bangalore | 4.5 ★ | ₹1,400 for two | Asian, Chinese | "Trendy option with high ratings; slightly premium but still within medium budget for a special outing." |

---

## Layout & responsive behavior

**Desktop (≥1024px):**

- Max content width ~1200px, centered
- Form: 2 columns (location/budget left, cuisine/rating right)
- Results: single column stacked cards OR 2-column grid for cards #2–#5

**Tablet (768–1023px):**

- Form stacks to 1 column
- Cards full width

**Mobile (≤767px):**

- Sticky bottom CTA optional
- Cards full bleed with padding
- Rating moves to top-right of card header
- Slider and stepper touch-friendly (min 44px tap targets)

---

## Components to define in design system

1. Primary / secondary buttons
2. Dropdown with search
3. Segmented budget control
4. Rating slider with star preview
5. Text area with helper text
6. Recommendation card (default + featured #1 variant)
7. Cuisine & budget chips
8. AI explanation callout
9. Info / warning / error banners
10. Loading skeleton cards
11. Empty state illustration block
12. Rank badge (#1 gold accent)

---

## UX principles (must follow)

1. **Explainability first** — AI "Why this pick" must be visually distinct and easy to scan
2. **Scannable results** — Name, rating, cost visible without expanding
3. **Trust signals** — Show that results come from real filtered data, not hallucinated venues
4. **Progressive disclosure** — Debug/meta details hidden in expander
5. **Accessibility** — WCAG-friendly contrast, clear focus states, readable font sizes
6. **No chat UI** — This is a form → results product, not a chatbot interface
7. **Bangalore-first** — Copy and examples should feel local (₹ pricing, Indian areas/cuisines)

---

## Technical constraints (for handoff)

- Output should work as a **React + Tailwind** or **React + CSS modules** implementation later
- Single page, no auth, no navigation drawer needed for MVP
- Form fields map 1:1 to API:
  - `location`, `budget` (low\|medium\|high), `cuisine`, `min_rating`, `additional_preferences`, `top_k`
- API response shape: `{ summary, recommendations[{ rank, restaurant, explanation }], meta }`
- Do **not** design: user login, checkout, maps, or order placement

---

## Deliverables requested from Stitch

1. **Desktop mockup** — full page: form + results
2. **Mobile mockup** — form + one result card
3. **Component sheet** — buttons, inputs, cards, banners, chips
4. **All UI states** — default, loading, success, empty, error, AI fallback banner
5. **Color, type, spacing tokens** for developer handoff

---

## What to avoid

- Generic purple-gradient "AI startup" look
- Dense admin dashboard layouts
- Chat bubble interfaces
- Dark mode only (light mode primary; dark optional)
- Cluttered forms with too many visible fields at once
- Stock photos that look obviously fake

---

## Final instruction to Stitch

Create a **beautiful, Zomato-inspired, AI-enhanced restaurant discovery UI** that feels ready for a portfolio demo. Prioritize clarity, appetite appeal, and trust in AI explanations. Make the #1 recommendation feel special. Keep the form friendly and fast to complete.

---

## Related project docs

- [context.md](./context.md) — product overview and workflow
- [architecture.md](../architecture.md) — technical architecture, API, and presentation layer spec
