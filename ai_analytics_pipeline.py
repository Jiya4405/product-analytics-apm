"""
Decision Center pipeline: recomputes the weekly 2FA incident metrics from
sql/03_2fa_incident_detection.sql in pandas (so this runs standalone against
the CSV without a SQL engine) and asks Claude for a root-cause brief - not
just a chart caption - naming the June 2026 2FA rollout as the likely cause,
the next KPI to watch, and the highest-leverage experiment to run.

Only aggregated weekly counts are sent to Claude, never raw user rows or
user_id values - see PRD.md "Privacy Compliance" and dashboard.html's
"Why aggregate before sending to Claude?" note for the privacy/cost/latency
trade-off this implies.
"""

import os

import pandas as pd

DATA_PATH = "data/raw_user_clickstream.csv"


def compute_weekly_2fa_metrics(df):
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])
    df["week_start"] = df["event_timestamp"].dt.to_period("W").dt.start_time

    weekly = (
        df[df["event_type"].isin(["login_2fa_challenge", "login_2fa_failed"])]
        .groupby(["week_start", "event_type"])
        .size()
        .unstack(fill_value=0)
    )
    for col in ("login_2fa_challenge", "login_2fa_failed"):
        if col not in weekly.columns:
            weekly[col] = 0

    total = weekly["login_2fa_challenge"] + weekly["login_2fa_failed"]
    weekly["failure_rate_pct"] = (weekly["login_2fa_failed"] / total.replace(0, pd.NA) * 100).round(2)
    return weekly


def build_prompt(weekly_metrics):
    return f"""You are a Decision Center for a Product Manager investigating a retention regression on a B2B SaaS analytics platform. Mandatory 2FA rolled out June 1, 2026.

Weekly 2FA challenge/failure counts since rollout:

{weekly_metrics.to_string()}

Answer as a root-cause brief, not a chart caption:
1. Root cause: what is the most likely cause of the failure-rate pattern above, and how confident are you (low/medium/high)?
2. Next KPI to monitor: which single downstream metric would confirm or rule this out fastest?
3. Highest-leverage experiment: one concrete product change, who owns shipping it, and the metric that would call it a win.
4. Weakest assumption: what part of this analysis is most likely wrong, and what data would tighten it?
"""


def main():
    df = pd.read_csv(DATA_PATH)
    weekly_metrics = compute_weekly_2fa_metrics(df)

    print("Weekly 2FA metrics:")
    print(weekly_metrics)

    prompt = build_prompt(weekly_metrics)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\nANTHROPIC_API_KEY not set - skipping live AI call. Prompt that would be sent:\n")
        print(prompt)
        return

    from anthropic import Anthropic, AnthropicError

    client = Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
    except AnthropicError as e:
        print(f"\nClaude API call failed ({e}) - falling back to the raw metrics table above.")
        print("The Decision Center prompt that would have been sent:\n")
        print(prompt)
        return

    print("\nAI Product Copilot summary:\n")
    print(response.content[0].text)


if __name__ == "__main__":
    main()
