WITH risk AS (
    SELECT * FROM {{ ref('fct_spoilage_risk') }}
),
prices AS (
    SELECT * FROM {{ ref('stg_commodity_prices') }}
)
SELECT
    r.container_id,
    r.commodity,
    r.origin,
    r.destination,
    r.telemetry_at,
    r.container_health_status,
    p.primary_price_usd,
    p.secondary_price_usd,
    ROUND(p.primary_price_usd * (1 - r.hourly_spoilage_rate), 2) AS expected_primary_payout_usd,
    ROUND(p.secondary_price_usd - (p.primary_price_usd * (1 - r.hourly_spoilage_rate)), 2) AS arbitrage_margin_usd,
    CASE
        WHEN (p.secondary_price_usd - (p.primary_price_usd * (1 - r.hourly_spoilage_rate))) > 0 THEN 'RECOMMEND_REROUTE'
        ELSE 'MAINTAIN_ROUTE'
    END AS decision_action
FROM risk r
JOIN prices p ON r.commodity = p.commodity