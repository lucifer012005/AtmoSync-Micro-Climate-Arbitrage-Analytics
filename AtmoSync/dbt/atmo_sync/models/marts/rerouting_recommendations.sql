WITH container_data AS (

    SELECT *
    FROM {{ ref('spoilage_arbitrage') }}

),

alternative_markets AS (

    SELECT
        c.CONTAINER_ID,
        c.COMMODITY,
        c.ORIGIN,
        c.DESTINATION AS CURRENT_DESTINATION,
        c.TEMPERATURE_C,
        c.HUMIDITY_PCT,
        c.CONTAINER_STATUS,

        r.MARKET AS ALTERNATIVE_MARKET,
        r.DISTANCE_KM,
        r.TRAVEL_TIME_HOURS,

        p.PRICE_PER_KG,
        p.QUALITY_PREMIUM

    FROM container_data c

    JOIN {{ source('raw', 'ROUTE_DISTANCES') }} r
        ON c.ORIGIN = r.ORIGIN

    LEFT JOIN {{ source('raw', 'COMMODITY_PRICES') }} p
        ON c.COMMODITY = p.COMMODITY
        AND r.MARKET = p.MARKET

    WHERE r.MARKET <> c.DESTINATION

),

ranked AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY CONTAINER_ID
            ORDER BY
                CASE
                    WHEN CONTAINER_STATUS = 'AT RISK'
                    THEN TRAVEL_TIME_HOURS
                    ELSE DISTANCE_KM
                END
        ) AS ROUTE_RANK

    FROM alternative_markets

)

SELECT
    CONTAINER_ID,
    COMMODITY,
    ORIGIN,
    CURRENT_DESTINATION,
    ALTERNATIVE_MARKET,
    TEMPERATURE_C,
    HUMIDITY_PCT,
    CONTAINER_STATUS,
    DISTANCE_KM,
    TRAVEL_TIME_HOURS,
    PRICE_PER_KG,
    QUALITY_PREMIUM,

    CASE
        WHEN CONTAINER_STATUS = 'AT RISK'
             AND ROUTE_RANK = 1
        THEN 'REROUTE RECOMMENDED'

        WHEN CONTAINER_STATUS = 'WARNING'
             AND ROUTE_RANK = 1
        THEN 'CONSIDER REROUTE'

        ELSE 'NO ACTION'
    END AS REROUTE_RECOMMENDATION

FROM ranked
WHERE ROUTE_RANK = 1