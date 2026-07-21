-- Cohort retention segmented by plan tier -- powers the plan-tier filter on
-- dashboard.html. Confirms the June retention drop isn't a single-segment
-- pricing/product issue: it holds across free, pro, and enterprise cohorts.
-- Swap or drop the WHERE clause to change the segment.
WITH tiered AS (
    SELECT r.*, u.plan_tier
    FROM raw_user_clickstream r
    JOIN (
        SELECT user_id, plan_tier FROM raw_user_clickstream WHERE event_type = 'signup'
    ) u ON r.user_id = u.user_id
),
user_monthly_activity AS (
    SELECT user_id, plan_tier, DATE_TRUNC('month', event_timestamp) AS activity_month
    FROM tiered
    GROUP BY 1, 2, 3
),
cohort_birth_months AS (
    SELECT user_id, plan_tier, MIN(activity_month) AS cohort_month
    FROM user_monthly_activity
    GROUP BY 1, 2
),
counts AS (
    SELECT
        c.cohort_month,
        c.plan_tier,
        DATEDIFF('month', c.cohort_month, a.activity_month) AS months_since_signup,
        COUNT(DISTINCT a.user_id) AS retained_users
    FROM cohort_birth_months c
    JOIN user_monthly_activity a ON c.user_id = a.user_id AND c.plan_tier = a.plan_tier
    WHERE c.plan_tier = 'pro'  -- or 'free' / 'enterprise'; remove this line for all tiers combined
    GROUP BY 1, 2, 3
),
month0 AS (
    SELECT cohort_month, retained_users AS cohort_size FROM counts WHERE months_since_signup = 0
)
SELECT
    c.cohort_month,
    c.plan_tier,
    c.months_since_signup,
    c.retained_users,
    ROUND(c.retained_users * 100.0 / m.cohort_size, 1) AS retention_pct
FROM counts c
JOIN month0 m ON c.cohort_month = m.cohort_month
WHERE c.months_since_signup <= 2
ORDER BY 1, 3;
