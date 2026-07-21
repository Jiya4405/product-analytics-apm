-- Daily Active Users, Monthly Active Users, and Product Stickiness (DAU/MAU) by plan tier
-- Source: data/raw_user_clickstream.csv loaded as table raw_user_clickstream
WITH daily_active AS (
    SELECT
        DATE(event_timestamp) AS event_date,
        plan_tier,
        COUNT(DISTINCT user_id) AS dau
    FROM raw_user_clickstream
    GROUP BY 1, 2
),
monthly_active AS (
    SELECT
        DATE_TRUNC('month', event_timestamp) AS event_month,
        plan_tier,
        COUNT(DISTINCT user_id) AS mau
    FROM raw_user_clickstream
    GROUP BY 1, 2
)
SELECT
    d.event_date,
    d.plan_tier,
    d.dau,
    m.mau,
    ROUND((d.dau::NUMERIC / m.mau::NUMERIC) * 100, 2) AS stickiness_pct
FROM daily_active d
JOIN monthly_active m
  ON DATE_TRUNC('month', d.event_date) = m.event_month
  AND d.plan_tier = m.plan_tier
ORDER BY d.event_date DESC, d.plan_tier;
