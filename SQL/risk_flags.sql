USE risk_monitoring;

-- Query 1: Which team and region has the most SLA breaches?
-- This tells us exactly where the biggest problems are

SELECT
    team,
    region,
    COUNT(order_id) AS total_orders,
    SUM(sla_breach) AS total_breaches,
    ROUND(SUM(sla_breach) * 100.0 / COUNT(order_id), 1) AS breach_rate_pct
FROM operations
GROUP BY team, region
ORDER BY breach_rate_pct DESC;

-- Query 2: Early Warning System
-- If efficiency dropped 3 months in a row, I flag it

SELECT
    team,
    month,
    ROUND(AVG(efficiency_score), 2) AS efficiency,
    ROUND(LAG(AVG(efficiency_score), 1) OVER (PARTITION BY team ORDER BY month), 2) AS last_month,
    ROUND(LAG(AVG(efficiency_score), 2) OVER (PARTITION BY team ORDER BY month), 2) AS two_months_ago,
    CASE
        WHEN AVG(efficiency_score) < LAG(AVG(efficiency_score), 1) OVER (PARTITION BY team ORDER BY month)
        AND  LAG(AVG(efficiency_score), 1) OVER (PARTITION BY team ORDER BY month) < LAG(AVG(efficiency_score), 2) OVER (PARTITION BY team ORDER BY month)
        THEN 'WARNING - dropping for 3 months'
        ELSE 'stable'
    END AS trend
FROM operations
GROUP BY team, month
ORDER BY team, month;

-- Query 3: Big orders that are stuck in delay

SELECT
    order_id,
    date,
    region,
    team,
    ROUND(revenue_clean, 2) AS revenue,
    processing_time_hrs,
    status
FROM operations
WHERE is_delayed = 1
AND revenue_clean > (SELECT AVG(revenue_clean) * 1.5 FROM operations)
ORDER BY revenue_clean DESC
LIMIT 50;