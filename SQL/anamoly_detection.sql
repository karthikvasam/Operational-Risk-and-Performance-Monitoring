USE risk_monitoring;
-- Query 1: Find orders where revenue is unusually high
-- If an order is more than 3x the standard deviation away, it is an anomaly

SELECT
    order_id,
    date,
    region,
    team,
    revenue_clean,
    status,
    ROUND(revenue_clean - AVG(revenue_clean) OVER (PARTITION BY region), 2) AS diff_from_avg
FROM operations
WHERE revenue_clean > (
    SELECT AVG(revenue_clean) + 3 * STDDEV(revenue_clean)
    FROM operations
)
ORDER BY revenue_clean DESC;

-- Query 2: Find orders that took too long to process
-- Anything above 3 standard deviations from average processing time is flagged

SELECT
    order_id,
    date,
    team,
    region,
    processing_time_hrs,
    status
FROM operations
WHERE processing_time_hrs > (
    SELECT AVG(processing_time_hrs) + 3 * STDDEV(processing_time_hrs)
    FROM operations
)
ORDER BY processing_time_hrs DESC;

-- Query 3: Check if any team's delay rate went up compared to last month
-- LAG means "get the previous row's value"

SELECT
    team,
    month,
    ROUND(AVG(is_delayed) * 100, 1) AS delay_rate_this_month,
    ROUND(
        LAG(AVG(is_delayed) * 100) OVER (PARTITION BY team ORDER BY month),
        1
    ) AS delay_rate_last_month
FROM operations
GROUP BY team, month
ORDER BY team, month;