# Retention Investigation Studio

A self-directed portfolio project simulating a B2B SaaS product analytics pipeline — from raw clickstream data through Lakehouse-style SQL modeling to a Decision Center that names a root cause, a recommended experiment, and an owner, not just a chart.

**Built for:** Product Managers investigating retention regressions after authentication changes.

**Live dashboard:** https://jiya4405.github.io/product-analytics-apm/

**All data in this repo is synthetically generated** (`generate_clickstream_data.py`, seeded for reproducibility) — this project demonstrates the analytics workflow and PM reasoning end to end, not real production telemetry.

## The scenario

420 simulated users sign up across Jan–Jun 2026 monthly cohorts. Mandatory 2FA rolls out June 1, 2026. Cohorts active during and after the rollout show extra churn and a spike in `login_2fa_failed` events — an authentication friction point a PM would need to catch and diagnose.

## Pipeline

```
generate_clickstream_data.py  ->  data/raw_user_clickstream.csv (Bronze)
                                          |
                                          v
                              sql/*.sql   (Silver/Gold metric views)
                                          |
                                          v
                          ai_analytics_pipeline.py  ->  Claude-generated
                                                          executive summary
```

## Repo layout

- `generate_clickstream_data.py` — generates the synthetic ~10K-row clickstream dataset into `data/`.
- `data/` — generated CSVs (`raw_user_clickstream.csv`, `users_reference.csv`).
- `sql/` — Gold-layer analytics queries:
  - `01_cohort_retention.sql` — month-over-month cohort retention (window functions + CTEs).
  - `02_dau_mau_stickiness.sql` — DAU/MAU product stickiness by plan tier.
  - `03_2fa_incident_detection.sql` — weekly 2FA failure rate, surfaces the June incident.
  - `04_retention_by_plan_tier.sql` — retention segmented by plan tier, confirms the drop isn't a single-segment issue; powers the dashboard's plan-tier filter.
- `PRD.md` — product requirement doc for the analytics engine (metrics, architecture rationale, guardrails).
- `ai_analytics_pipeline.py` — sends the aggregated weekly 2FA metrics to Claude and asks for a root-cause brief (root cause + confidence, next KPI to watch, highest-leverage experiment, weakest assumption) rather than a chart caption. Falls back to printing the prompt if the key is missing or the API call fails.
- `dashboard.html` — a self-contained HTML "Decision Center" (no build step): a root-cause card with evidence, recommended action, and an experiment backlog sit above the charts, not below them. Includes a real plan-tier filter, collapsible SQL under each chart, an architecture/trade-offs section, and the AI copilot panel. Built directly against real DuckDB query output, in place of Power BI / Figma since neither tool is scriptable from this environment. Open it directly in a browser.
- `FIGMA_WIREFRAME_GUIDE.md` — step-by-step spec if you want to build a native Figma version by hand.

## Running it

```bash
pip install -r requirements.txt
python3 generate_clickstream_data.py     # writes data/*.csv

# SQL layer — verified against DuckDB:
python3 -c "import duckdb; con = duckdb.connect(); con.execute(\"CREATE TABLE raw_user_clickstream AS SELECT * FROM read_csv_auto('data/raw_user_clickstream.csv')\"); print(con.execute(open('sql/01_cohort_retention.sql').read()).df())"

export ANTHROPIC_API_KEY=your-key-here   # optional; without it, the prompt is printed instead
python3 ai_analytics_pipeline.py

open dashboard.html   # or just double-click it
```

## Verified results (this seeded run)

- Jan–Mar cohorts' month-1 retention: 64–67%. May cohort (first full month is the 2FA rollout month): **32.9%** — the incident the AI copilot is built to catch.
- Weekly 2FA challenge failure rate since rollout: **~25% average**, peaking at 50% (vs a 10% reliability floor in the PRD).
- Product stickiness (DAU/MAU) declined from 13.4% in January to 9.8% in July, against a 25% target.

## Next steps

- Wire `dashboard.html`'s copilot input to a real backend call into `ai_analytics_pipeline.py` (currently a static sample response, clearly labeled as such).
- Port the local CSV read to a real Delta Lake table on a Databricks workspace.
- Optional: rebuild `dashboard.html`'s layout in Power BI or Figma by hand using `FIGMA_WIREFRAME_GUIDE.md` if you want native tool files for your portfolio.
