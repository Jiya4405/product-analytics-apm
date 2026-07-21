"""
Simulated raw clickstream generator for the Databricks-Inspired Product Analytics project.

Produces data/raw_user_clickstream.csv — the "Raw User Clickstream CSVs" box in the
pipeline diagram, meant to be cleaned with Python/PySpark and loaded into Delta Lake
Silver/Gold tables downstream.

Story baked into the data: users sign up across Jan-Jun 2026 monthly cohorts, retention
decays normally month over month, but the 2026-05 cohort takes an extra churn hit in its
first retention month (June 2026) because that's when mandatory 2FA rolled out — this
mirrors the "60% drop" scenario used later in the AI Product Copilot prompt.
"""

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

COHORT_MONTHS = pd.date_range("2026-01-01", "2026-06-01", freq="MS")
OBSERVATION_END = pd.Timestamp("2026-07-31")
TWO_FA_ROLLOUT = pd.Timestamp("2026-06-01")

USERS_PER_COHORT = 70
BASE_MONTHLY_RETENTION = 0.72
TWO_FA_EXTRA_CHURN = 0.55  # additional drop applied to the retention month that lands on/after rollout

PLAN_TIERS = ["free", "pro", "enterprise"]
PLAN_WEIGHTS = [0.55, 0.35, 0.10]
PLATFORMS = ["web", "desktop", "mobile"]
PLATFORM_WEIGHTS = [0.65, 0.25, 0.10]

FEATURE_EVENTS = [
    "notebook_run",
    "sql_editor_query",
    "dashboard_view",
    "delta_live_tables_edit",
    "mlflow_experiment",
    "job_scheduler_create",
    "cluster_start",
]


def build_users():
    users = []
    user_id = 1
    for cohort_month in COHORT_MONTHS:
        for _ in range(USERS_PER_COHORT):
            signup_day_offset = int(RNG.integers(0, 28))
            signup_date = cohort_month + pd.Timedelta(days=signup_day_offset)
            users.append(
                {
                    "user_id": user_id,
                    "cohort_month": cohort_month,
                    "signup_timestamp": signup_date,
                    "plan_tier": RNG.choice(PLAN_TIERS, p=PLAN_WEIGHTS),
                }
            )
            user_id += 1
    return pd.DataFrame(users)


def months_active(cohort_month, signup_timestamp):
    """Return the list of activity months a user is retained for, applying decay and the 2FA shock."""
    active_months = [cohort_month]
    retention_prob = BASE_MONTHLY_RETENTION
    current_month = cohort_month
    while True:
        current_month = current_month + pd.DateOffset(months=1)
        if current_month > OBSERVATION_END:
            break
        month_retention_prob = retention_prob
        if current_month >= TWO_FA_ROLLOUT and cohort_month < TWO_FA_ROLLOUT:
            month_retention_prob = retention_prob * (1 - TWO_FA_EXTRA_CHURN)
        if RNG.random() < month_retention_prob:
            active_months.append(current_month)
            retention_prob = min(retention_prob * 1.05, 0.9)  # users who survive one more month churn a bit less going forward
        else:
            break
    return active_months


def build_events(users_df):
    events = []
    event_id = 1
    for _, user in users_df.iterrows():
        active_months = months_active(user["cohort_month"], user["signup_timestamp"])

        events.append(
            {
                "event_id": event_id,
                "user_id": user["user_id"],
                "event_timestamp": user["signup_timestamp"],
                "event_type": "signup",
                "feature_name": None,
                "platform": RNG.choice(PLATFORMS, p=PLATFORM_WEIGHTS),
                "plan_tier": user["plan_tier"],
            }
        )
        event_id += 1

        for month in active_months:
            sessions_this_month = int(RNG.integers(1, 6))
            for _ in range(sessions_this_month):
                day_offset = int(RNG.integers(0, 27))
                session_ts = month + pd.Timedelta(days=day_offset, hours=int(RNG.integers(7, 22)))
                platform = RNG.choice(PLATFORMS, p=PLATFORM_WEIGHTS)

                login_event_type = "login"
                if month >= TWO_FA_ROLLOUT and RNG.random() < 0.30:
                    login_event_type = "login_2fa_challenge"
                    if RNG.random() < 0.20:
                        events.append(
                            {
                                "event_id": event_id,
                                "user_id": user["user_id"],
                                "event_timestamp": session_ts,
                                "event_type": "login_2fa_failed",
                                "feature_name": None,
                                "platform": platform,
                                "plan_tier": user["plan_tier"],
                            }
                        )
                        event_id += 1
                        continue  # failed 2FA aborts the session before any feature usage

                events.append(
                    {
                        "event_id": event_id,
                        "user_id": user["user_id"],
                        "event_timestamp": session_ts,
                        "event_type": login_event_type,
                        "feature_name": None,
                        "platform": platform,
                        "plan_tier": user["plan_tier"],
                    }
                )
                event_id += 1

                feature_actions = int(RNG.integers(1, 5))
                for _ in range(feature_actions):
                    action_ts = session_ts + pd.Timedelta(minutes=int(RNG.integers(1, 90)))
                    events.append(
                        {
                            "event_id": event_id,
                            "user_id": user["user_id"],
                            "event_timestamp": action_ts,
                            "event_type": "feature_use",
                            "feature_name": RNG.choice(FEATURE_EVENTS),
                            "platform": platform,
                            "plan_tier": user["plan_tier"],
                        }
                    )
                    event_id += 1

    return pd.DataFrame(events)


def main():
    users_df = build_users()
    events_df = build_events(users_df)
    events_df = events_df.sort_values("event_timestamp").reset_index(drop=True)

    print(f"Users generated: {len(users_df)}")
    print(f"Events generated: {len(events_df)}")
    print(events_df["event_type"].value_counts())

    events_df.to_csv("data/raw_user_clickstream.csv", index=False)
    users_df.to_csv("data/users_reference.csv", index=False)
    print("\nWrote data/raw_user_clickstream.csv and data/users_reference.csv")


if __name__ == "__main__":
    main()
