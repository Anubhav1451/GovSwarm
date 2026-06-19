# Premium UI/UX Design Tokens & Best Practices

Extracted from ui-ux-pro-max-skill repository and aligned with GovSwarm V2 existing patterns.

## Color Palette
- **Primary Cyan**: `#00E5FF` - used for neon accents, icons, highlights
- **Danger Red**: `#EF4444` - critical alerts, frozen assets
- **Success Green**: `#22C55E` - secure status, active indicators
- **Warning Amber**: `#F59E0B` - medium risk, pending reviews
- **Gray Neutral**: `#64748B` - secondary text, subtle borders
- **Dark Background**: `#050816` - main panel background
- **Slightly Lighter**: `#0F172A` - cards, dropdowns, containers
- **Footer Background**: `#0A0F24` - terminal/log input area
- **Off‑White Text**: `#F8FAFC` - primary body text
- **Pure White**: `#FFFFFF` - icons, highlights on dark

## Typography
- **Font Family**: `monospace` for dashboard UI
- **Letter Spacing**: `0.5px` for dense numeric/data display
- **Font Sizes**:
  - Header: `24px` fontWeight `900`
  - Subheader/Labels: `11px` - `14px`
  - Metrics Values: `18px` - `bold`
  - Small text / footnotes: `9px`
  - Terminal input: `13px`

## Layout & Grid System
- **Viewport Constraint**: `height: 100vh` (or `max-h-screen`) via outer container
- **Root Grid**: `display: grid; gridTemplateRows: auto 1fr auto; gap: 24px; padding: 24px;`
  - Row 1: Auto‑sized Top HUD
  - Row 2: Flexible main content (takes remaining vertical space)
  - Row 3: Auto‑sized Footer (terminal line)
- **Main Content Flex**: Three‑column layout using `display: flex; height: 100%;`
  - Left Column: `flex: 1 1 360px` (metrics matrix + stream logs)
  - Center Column: `flex: 1.8 1 500px` (Forensic Orb + details + graph)
  - Right Column: `flex: 1.2 1 400px` (control panel)
- **Gap & Padding**: Consistent `gap: 24px` between major sections; internal `padding: 16px`‑`24px` for cards.
- **Border Radius**: `8px`‑`24px` depending on card prominence (orb uses `24px`).

## Neon & Glow Effects
- **Neon Border**: `1px solid rgba(0,229,255,0.3)` (vary opacity for depth)
- **Outer Glow**: `box-shadow: 0 0 25px rgba(0,229,255,0.2), inset 0 0 15px rgba(0,229,255,0.2)` (pulsed via animation)
- **Inner Glow**: Use `blur` or multiple shadow layers.
- **Gradient Borders**: `conic-gradient` or `radial-gradient` animated for orbital effects.

## Animations & Micro‑Interactions
Define in a central `<AnimationStyles />` component (or CSS keyframes):
- `spinCW` / `spinCCW`: Continuous rotation for rings.
- `pulseNeon`: Scale + opacity pulse for core orb.
- `pulseGlow`: Breathing glow for containers.
- `orbitCW` / `orbitCCW`: Alternating speed ring animations.
- `radarSweep`: Sweeping opacity/rotate for scanning feel.
- `scanline`: Horizontal line moving vertically.
- `coreBreathe`: Scale + drop‑shadow pulse.
- `blink`: Opacity toggle for critical banner (used in frozen assets overlay).
- `slideInRight`: Toast entrance transition.

## Component‑Level Patterns
### Metrics Card
- Background: `#050816` with thin border `rgba(255,255,255,0.02)`.
- Radius: `8px`.
- Padding: `12px`.
- Two‑line label/value layout: small caption (`9px`, `#64748B`) → large value (`18px`, `bold`, color‑coded) → unit/footer (`9px`, color‑specific).
- Hover/active states not required but can add subtle scale.

### Streaming Logs Container
- Dark background `#050816`, radius `8px`, padding `12px`.
- Fixed height (`190px`) with `overflowY: auto`.
- Monospace font, size `10px`, color `#38BDF8`.
- Scanline overlay: `linear-gradient(to bottom, transparent 45%, rgba(0,229,255,0.02) 50%, transparent 55%)` animated.
- Messages colored by severity:
  - Critical/Breach/🚨: `#EF4444`
  - Warning/⚠️: `#F59E0B`
  - Default: `#38BDF8`

### Forensic Orb (Centerpiece)
- Base: `radial-gradient(circle at center, #0B132B 0%, #050816 100%)`.
- Nebula rings:
  - Dashed outer: `border: 2px dashed rgba(0,229,255,0.5); animation: spinCW 16s linear infinite;`
  - Dotted middle: `border: 2px dotted rgba(239,68,68,0.4); animation: spinCCW 10s linear infinite;`
  - Conic gradient slice: `background: conic-gradient(from 0deg, rgba(0,229,255,0.08) 0deg, transparent 120deg); animation: spinCW 5s linear infinite;`
- Core: `radial-gradient(circle, #00E5FF 0%, #0F172A 75%)` with solid neon border `3px solid #00E5FF`, size `70px`, animation `pulseNeon 2s ease-in-out infinite`.
- Label: neon cyan text `CORE`, `11px`, bold, letter‑spacing `0.05em`.
- Optional Frozen Overlay: absolute inset `0`, flex center, text `[ASSETS FROZEN]`, red `#FF0000`, text‑shadow `0 0 10px rgba(255,0,0,0.7)`, animation `blink 1s ease-in-out infinite`.

## Status Indicators
- **Secure Mesh Gateway**: Green dot (`width:8px;height:8px;border-radius:50%;background:#22C55E;box-shadow:0 0 8px #22C55E`) + label.
- **GST / PAN Status**: Text with check/cross emoji; color derived from status (green for ✓, red for ❌).
- **MCA Status**: Text with appropriate color (red for breach, green for clear, amber for warning).

## Interactive Elements
- **Dropdown (`<select>`)**: Transparent background, no border, white text, width `240px`, monospace, cursor pointer.
- **Mic Button**: Circular background `rgba(0,229,255,0.1)` (idle) or `rgba(239,68,68,0.1)` (listening), padded, border‑radius `50%`.
- **Action Buttons**: Transparent base with colored border (`rgba(...);`), text matching border color, `borderRadius:4px`, `padding:2px 6px`, `fontSize:9px`.
- **Primary Action** (e.g., Trigger Enforcement): Solid background (`#EF4444`), white text, `borderRadius:6px`, `fontWeight:bold`, `fontFamily:monospace`, `letterSpacing:1px`.

## Toast & Banner
- **Critical Toast**: Fixed top‑right, `background: rgba(239,68,68,0.9)`, `color: white`, `padding:12px 20px`, `borderRadius:8px`, `fontSize:14px`, `fontWeight:bold`, `boxShadow:0 0 20px rgba(239,68,68,0.7)`, animation `slideInRight 0.3s ease-out`.
- **Frozen Overlay Banner**: As used on orb, absolute centered, blinking red text.

## Responsive Considerations (Current Fixed‑Size Design)
- Designed for desktop‑scale monitors; breakpoints not implemented.
- If responsiveness needed, reduce font sizes and gap/padding on widths `< 1024px` using media queries.
- Orb diameter and container flex ratios may adjust.

## Implementation Guidelines
1. **Centralize Animations**: Keep all `@keyframes` in a single `<AnimationStyles />` component reused via inline `<style>`.
2. **Semantic Naming**: Use CSS class‑like naming in JSX style objects for readability (e.g., `styles.metricsCard`).
3. **Theme Tokens**: Consider extracting repeated color/size values to JavaScript constants for easier theming.
4. **Accessibility**: Ensure sufficient contrast (neon cyan on dark passes; red on dark may need verification). Add `aria‑label` where icons convey meaning.
5. **Performance**: Animations run efficiently via CSS; limit number of simultaneously animating elements to avoid jank.
6. **Layering**: Use `zIndex` intentionally (modal banner `9999`, toast `1000`, orbiting rings `10`).

--- 
*This document serves as the mandatory visual guideline for all frontend tasks in GovSwarm V2.*