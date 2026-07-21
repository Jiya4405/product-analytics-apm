# Figma Wireframe Guide: Product Analytics Dashboard

Goal: a low-fidelity wireframe showing a PM logging in, viewing cohort retention data, and asking the AI copilot about it — the "Power BI Dashboard / Figma Wireframe UI" step in the pipeline, paired with the "Ask AI about this cohort's behavior" copilot from `ai_analytics_pipeline.py`.

## 1. New file setup

1. Figma → New design file. Rename it `Product Analytics Dashboard — Wireframe`.
2. Create a frame: `Desktop` preset, 1440×1024.
3. Set up a basic grid: 12 columns, 24px gutter, 80px margin (Layout Grid panel, `Shift+G`).

## 2. Page structure (top to bottom)

### A. Top nav bar (height 64px)
- Left: product wordmark/logo placeholder (rectangle + text "Analytics Engine").
- Right: user avatar circle + plan tier badge (e.g. "Enterprise").

### B. Left sidebar (width 240px, full height below nav)
- Nav items as simple text rows with icon placeholders (16×16 squares):
  - Overview
  - Cohort Retention (mark as active/selected state)
  - DAU / MAU
  - 2FA & Reliability
  - Settings

### C. Main content area
Split into two stacked sections.

**Section 1 — Retention chart (top ~55% of content area)**
- Header row: title "Cohort Retention" (left) + month-range filter dropdown placeholder (right).
- Chart placeholder: a line chart, one line per cohort (Jan–Jun 2026), x-axis = "Months since signup" (0–2), y-axis = "% retained." Sketch 6 lines with the Jan–May cohorts curving gently down, and the June-launch (2FA rollout) causing a visibly steeper dip for cohorts crossing that month — this is the visual hook that should make a viewer want to click "Ask AI."
- Small stat tiles row beneath the chart: "Month-1 Retention: 42%", "Stickiness (DAU/MAU): 22%", "2FA Failure Rate: 24%" — pull these numbers from `sql/01_cohort_retention.sql`, `sql/02_dau_mau_stickiness.sql`, and `sql/03_2fa_incident_detection.sql` once you run them, so the wireframe reflects your real synthetic data rather than placeholder numbers.

**Section 2 — AI Copilot panel (bottom ~45%, or a right-side drawer if you prefer a split layout)**
- Panel header: "Ask AI about this cohort's behavior" (this is the literal empty text box from the original spec).
- Empty input field, placeholder text: "e.g. Why did the May cohort's retention drop?"
- Below the input: a response card (mocked) showing the 3-bullet format your pipeline actually generates:
  1. Which week/cohort shows the anomaly
  2. The likely friction point (2FA rollout)
  3. A recommended experiment
- Add a small "Powered by Claude" tag near the input to signal the AI integration honestly.

## 3. Interaction notes (annotate directly on the frame)

- Clicking a cohort line in the chart should filter/highlight the AI panel's context to that cohort (note this as an arrow + text annotation, no need to build real interactivity in a wireframe).
- The input box submits to `ai_analytics_pipeline.py`'s prompt-building logic — annotate this with a comment: "Submits cohort + metric context to Claude API, returns 3-bullet summary."

## 4. Fidelity level

Keep this at wireframe fidelity: grayscale, placeholder rectangles for charts (or Figma's native line chart via a plugin like "Chart" if you want it to look more real), system font, no real branding. The goal is to prove you can go from data → UI concept → AI feature, not to ship pixel-perfect visual design.

## 5. Exporting for your portfolio

- Frame → Export as PNG (2x) for a static screenshot in your README/portfolio.
- Or share the Figma file link directly (Figma → Share → set to "Anyone with the link can view").
- Add the screenshot/link to this repo's `README.md` under a new "## UI Wireframe" section once it's built.
