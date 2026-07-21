-- Calculate Month-over-Month User Retention Cohorts
-- Source: data/raw_user_clickstream.csv loaded as table raw_user_clickstream
WITH user_monthly_activity AS (
    SELECT
        user_id,
        DATE_TRUNC('month', event_timestamp) AS activity_month
    FROM raw_user_clickstream
    GROUP BY 1, 2
),
cohort_birth_months AS (
    SELECT
        user_id,
        MIN(activity_month) AS cohort_month
    FROM user_monthly_activity
    GROUP BY 1
)
SELECT
    c.cohort_month,
    DATEDIFF('month', c.cohort_month, a.activity_month) AS months_since_signup,
    COUNT(DISTINCT a.user_id) AS retained_users
FROM cohort_birth_months c
JOIN user_monthly_activity a ON c.user_id = a.user_id
GROUP BY 1, 2
ORDER BY 1, 2;
