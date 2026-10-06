WITH commodity_base AS (
    SELECT 'Avocado' AS commodity, 4.50 AS primary_price_usd, 3.80 AS secondary_price_usd
    UNION ALL
    SELECT 'Mango', 3.20, 2.70
    UNION ALL
    SELECT 'Banana', 1.80, 1.40
    UNION ALL
    SELECT 'Tomato', 2.10, 1.60
)
SELECT
    commodity,
    primary_price_usd,
    secondary_price_usd,
    CURRENT_DATE() AS effective_date
FROM commodity_base