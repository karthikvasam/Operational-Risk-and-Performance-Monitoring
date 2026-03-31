USE risk_monitoring;

-- Query 1: How did each month perform overall?
-- This is like a monthly report card for the business

SELECT
    month,
    COUNT(order_id) AS total_orders,
    ROUND(SUM(revenue_clean), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(profit_margin), 2) AS avg_profit_margin,
    ROUND(AVG(efficiency_score), 2) AS avg_efficiency
FROM operations
GROUP BY month
ORDER BY month;


-- Query 2: Is revenue going up or down month by month?
-- LAG gives me last month's revenue so I can compare

SELECT
    month,
    ROUND(SUM(revenue_clean), 2) AS this_month_revenue,
    ROUND(
        LAG(SUM(revenue_clean)) OVER (ORDER BY month),
        2
    ) AS last_month_revenue,
    ROUND(
        SUM(revenue_clean) - LAG(SUM(revenue_clean)) OVER (ORDER BY month),
        2
    ) AS revenue_difference
FROM operations
GROUP BY month
ORDER BY month;


-- Query 3: How is each region performing?
-- Comparing revenue, delays and efficiency across all regions

SELECT
    region,
    COUNT(order_id) AS total_orders,
    ROUND(SUM(revenue_clean), 2) AS total_revenue,
    ROUND(AVG(profit_margin), 2) AS avg_margin,
    ROUND(AVG(is_delayed) * 100, 1) AS delay_rate_pct,
    SUM(sla_breach) AS total_sla_breaches
FROM operations
GROUP BY region
ORDER BY total_revenue DESC;


-- Query 4: Which team is most efficient each month?
-- RANK gives position 1 to the best team that month

SELECT
    team,
    month,
    ROUND(AVG(efficiency_score), 2) AS avg_efficiency,
    RANK() OVER (
        PARTITION BY month
        ORDER BY AVG(efficiency_score) DESC
    ) AS rank_this_month
FROM operations
GROUP BY team, month
ORDER BY month, rank_this_month;