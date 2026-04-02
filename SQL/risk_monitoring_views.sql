USE risk_monitoring;

CREATE VIEW monthly_kpi_view AS
SELECT
    month,
    MIN(date) AS month_start_date,
    COUNT(order_id) AS total_orders,
    ROUND(SUM(revenue_clean), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(profit_margin), 2) AS avg_profit_margin,
    ROUND(AVG(efficiency_score), 2) AS avg_efficiency
FROM operations
GROUP BY month
ORDER BY MIN(date);

CREATE VIEW regional_kpi_view AS
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

CREATE VIEW anomaly_view AS
SELECT
    order_id,
    date,
    region,
    team,
    ROUND(revenue, 2) AS original_revenue,
    ROUND(revenue_clean, 2) AS cleaned_revenue,
    ROUND(revenue - revenue_clean, 2) AS amount_clipped,
    profit_margin,
    status
FROM operations
WHERE revenue_flag = 1
ORDER BY revenue DESC;

CREATE VIEW sla_risk_view AS
SELECT
    team,
    region,
    COUNT(order_id) AS total_orders,
    SUM(sla_breach) AS total_breaches,
    ROUND(SUM(sla_breach) * 100.0 / COUNT(order_id), 1) AS breach_rate_pct,
    ROUND(AVG(processing_time_hrs), 2) AS avg_processing_hrs
FROM operations
GROUP BY team, region
ORDER BY breach_rate_pct DESC;

CREATE VIEW early_warning_view AS
SELECT
    team,
    month,
    ROUND(AVG(efficiency_score), 2) AS efficiency,
    ROUND(LAG(AVG(efficiency_score), 1) OVER (PARTITION BY team ORDER BY month), 2) AS last_month,
    CASE
        WHEN AVG(efficiency_score) < LAG(AVG(efficiency_score), 1) OVER (PARTITION BY team ORDER BY month)
        AND LAG(AVG(efficiency_score), 1) OVER (PARTITION BY team ORDER BY month) < LAG(AVG(efficiency_score), 2) OVER (PARTITION BY team ORDER BY month)
        THEN 'WARNING'
        ELSE 'Stable'
    END AS trend
FROM operations
GROUP BY team, month
ORDER BY team, month;