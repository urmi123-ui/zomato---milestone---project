---
name: Gourmet Intelligence
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1b1b1b'
  on-surface-variant: '#5b403f'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0ef'
  outline: '#8f6f6e'
  outline-variant: '#e4bebc'
  surface-tint: '#bb162c'
  primary: '#b7122a'
  on-primary: '#ffffff'
  primary-container: '#db313f'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb3b1'
  secondary: '#7c5800'
  on-secondary: '#ffffff'
  secondary-container: '#feb700'
  on-secondary-container: '#6b4b00'
  tertiary: '#0058bd'
  on-tertiary: '#ffffff'
  tertiary-container: '#1470e8'
  on-tertiary-container: '#fefcff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#ffdea8'
  secondary-fixed-dim: '#ffba20'
  on-secondary-fixed: '#271900'
  on-secondary-fixed-variant: '#5e4200'
  tertiary-fixed: '#d8e2ff'
  tertiary-fixed-dim: '#adc6ff'
  on-tertiary-fixed: '#001a41'
  on-tertiary-fixed-variant: '#004494'
  background: '#fcf9f8'
  on-background: '#1b1b1b'
  surface-variant: '#e5e2e1'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '800'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  title-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 48px
---

## Brand & Style

The design system is engineered for a premium restaurant discovery experience that balances the visceral appeal of food with the sophisticated precision of AI. The brand personality is **trustworthy, appetizing, and smart**, avoiding the cold "tech-first" aesthetics of typical SaaS in favor of a warm, hospitable digital environment.

The design style is **Modern Professional**, characterized by high-quality typography, generous whitespace, and tactile depth. It utilizes a soft-layered approach where information is compartmentalized into clean cards and chips, ensuring that high-density data (ratings, distance, price, AI match scores) remains digestible and visually organized.

## Colors

The palette is anchored by a high-energy **Primary Coral**, used strategically for key actions and brand identification to stimulate appetite and urgency. 

- **Primary (#E23744):** Reserved for primary buttons, selection states, and brand marks.
- **Secondary Amber (#FFB800):** Used exclusively for social proof, including star ratings, "Top Choice" badges, and premium status indicators.
- **Tertiary Blue (#3A86FF):** A calm, informative accent used for utility banners, "AI Insight" tooltips, and map markers to distinguish logic from emotion.
- **Neutrals:** A deep charcoal (#1C1C1C) provides maximum contrast for legibility, while a warm off-white (#FAFAFA) background prevents the interface from feeling clinical.

## Typography

This design system utilizes **Plus Jakarta Sans** for its friendly yet precise geometric proportions. The typographic hierarchy is intentionally bold to handle the "scanning" behavior of hungry users.

- **Headlines:** Use heavy weights (700-800) with slight negative letter-spacing to create a "editorial" feel for restaurant names and section headers.
- **Body:** Set at 14px and 16px to maintain high readability. Paragraphs should use a generous line-height (1.5x) to ensure descriptions of dishes feel airy and inviting.
- **Labels:** Small, uppercase, semi-bold weights are used for metadata like "DISTANCE" or "CUISINE" to provide structure without distracting from primary content.

## Layout & Spacing

The layout follows a **Fluid Grid** model with a base unit of 4px. 

- **Mobile:** A 4-column grid with 16px margins. Content cards usually span the full width to prioritize large-scale food imagery.
- **Desktop:** A 12-column grid with a max-width of 1280px. Gutters are fixed at 24px to maintain breathability between search results and map views.
- **Spacing Philosophy:** Use "lg" (24px) spacing between distinct content sections and "sm" (8px) for internal card elements. This creates a clear visual grouping where metadata stays tight to its parent image.

## Elevation & Depth

Hierarchy is established through **Ambient Shadows** and tonal layering rather than heavy borders.

- **Level 0 (Background):** #FAFAFA. Used for the global canvas.
- **Level 1 (Cards/Sheets):** #FFFFFF with a very soft, diffused shadow (`y: 4, blur: 20, opacity: 0.05, color: #000`). This is the primary container for restaurant listings.
- **Level 2 (Active/Hover):** When a user interacts with a card, the shadow should deepen (`y: 8, blur: 24, opacity: 0.10`) to simulate the card lifting off the surface.
- **Overlays:** Modals and bottom sheets use a backdrop blur (12px) on the background to maintain context while focusing the user's attention.

## Shapes

The design system uses a **Rounded** shape language to evoke a friendly, approachable, and "organic" feel consistent with the food industry.

- **Standard (8px):** Used for small input fields and action buttons.
- **Large (16px):** The signature radius for all restaurant cards, category tiles, and bottom sheets.
- **Pill (100px):** Exclusively for tags/chips (e.g., "Open Now", "Vegan", "Trending") and the primary search bar. This distinct shape helps users identify "filters" at a glance.

## Components

### Buttons
- **Primary:** Coral background (#E23744) with white text. 16px radius.
- **Secondary:** White background with a thin 1px border (#E0E0E0).
- **AI Action:** Subtle gradient from Coral to a slightly lighter tint to highlight "Smart" features.

### Chips & Tags
- Metadata (Cuisine, Price Level) uses a light gray background (#F0F0F0) with Charcoal text.
- AI Match scores use a subtle Tertiary Blue tint (#EBF2FF) to highlight the "logic" behind the recommendation.

### Cards
- Restaurant cards are the hero component. They feature a top-heavy layout with a 16:9 aspect ratio image, followed by a tight grouping of title, rating (Secondary Amber), and AI summary. 16px corner radius is mandatory.

### Input Fields
- Search bars should be pill-shaped with a subtle inner shadow to look "inset." 
- Form fields use a 1px border (#E0E0E0) that thickens and changes to Primary Coral on focus.

### Ratings & Badges
- Ratings always appear in Bold Secondary Amber with a star icon. 
- "DineAI Choice" badges use a gold-foil effect (slight gradient) to denote premium status.