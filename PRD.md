# Product Requirement Document (PRD)

## Internal AI-Driven Product Analytics Engine (V1.0)

**Author:** Associate Product Manager candidate (self-directed portfolio project)
**Target Audience:** Engineering, Data Platform, Design
**Status:** Simulated project — all data below is synthetically generated (see `generate_clickstream_data.py`) to demonstrate the analytics workflow, not real user telemetry.

---

### 1. Product Vision & Problem Statement

Product Managers spend excessive time writing ad-hoc SQL and building one-off dashboards to explain drops in retention and engagement metrics. When a core metric breaks, tracing the root cause requires manually cross-referencing data logs against engineering release cycles.

**The Solution:** An internal analytics engine that continuously tracks user telemetry (Lakehouse Gold Layer), materializes it into retention/engagement metric views, and feeds those views to an LLM that generates a natural-language operational diagnosis a PM can act on immediately.

### 2. Core User Personas

- **The Executive PM** — needs a high-level read on product adoption trends (DAU/MAU, retention) without writing SQL.
- **The Platform Support Engineer** — needs immediate visibility into authentication/operational friction that maps back to a specific feature release window.

### 3. Core Product Metrics (KPIs)

- **Core Engagement Tracker:** Product Stickiness (DAU/MAU) — target > 25%.
- **Retention Floor:** Month-1 retention per cohort — target > 55%.
- **Platform Reliability Floor:** 2FA challenge failure rate — target < 10% of challenges issued.

### 4. Functional Specifications & Engineering Handoff

#### 4.1 System Event Telemetry Pipeline

```
┌───────────────────────────────┐
│ Raw User Clickstream (Bronze) │   data/raw_user_clickstream.csv
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────────┐
│ Parsed Telemetry (Silver)         │   user_id, event_type, feature_name,
│                                    │   platform, plan_tier, event_timestamp
└───────────────┬───────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│ Metrics Aggregations & Cohorts (Gold)    │   sql/01_cohort_retention.sql
│ Purpose: fast dashboard + AI copilot     │   sql/02_dau_mau_stickiness.sql
│ queries                                  │   sql/03_2fa_incident_detection.sql
└─────────────────────────────────────────┘
```

**Why Lakehouse (Delta Lake) over a traditional warehouse:** raw clickstream events are semi-structured (not every event has a `feature_name`), arrive continuously rather than in a nightly batch, and need to support both SQL analytics (Gold views) and ad-hoc reprocessing (e.g., Python/PySpark cleaning of Bronze data) on the same copy of the data. A Lakehouse pattern avoids maintaining separate storage for raw/streaming data and curated analytical tables.

#### 4.2 Cross-Functional Requirements & Guardrails

- **Data Latency:** Gold-layer materialization completes within a 15-minute processing window of new Bronze data landing.
- **Privacy Compliance:** `user_id` values are hashed before being included in any LLM prompt context — the AI copilot only ever sees aggregated counts, never raw user-level rows.

### 5. Known Incident Baked Into the Simulated Dataset

The synthetic data intentionally encodes a real-world PM scenario: mandatory 2FA rolled out June 1, 2026. Cohorts that signed up before the rollout show a sharper-than-normal drop in month-1 retention, and `login_2fa_failed` events spike starting that week — this is what `sql/03_2fa_incident_detection.sql` and the AI copilot (`ai_analytics_pipeline.py`) are designed to surface automatically.
