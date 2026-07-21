-- Weekly 2FA challenge failure rate: surfaces the June 2026 authentication
-- friction spike introduced when mandatory 2FA rolled out (see generate_clickstream_data.py).
-- Source: data/raw_user_clickstream.csv loaded as table raw_user_clickstream
SELECT
    DATE_TRUNC('week', event_timestamp) AS week_start,
    COUNT(CASE WHEN event_type = 'login_2fa_challenge' THEN 1 END) AS challenges_issued,
    COUNT(CASE WHEN event_type = 'login_2fa_failed' THEN 1 END) AS challenges_failed,
    ROUND(
        COUNT(CASE WHEN event_type = 'login_2fa_failed' THEN 1 END)::NUMERIC
        / NULLIF(
            COUNT(CASE WHEN event_type IN ('login_2fa_challenge', 'login_2fa_failed') THEN 1 END),
            0
          )::NUMERIC * 100,
        2
    ) AS two_fa_failure_rate_pct
FROM raw_user_clickstream
GROUP BY 1
ORDER BY 1;
