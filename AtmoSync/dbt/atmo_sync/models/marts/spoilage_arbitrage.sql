WITH sensor_data AS (

    SELECT *
    FROM {{ ref('stg_iot_telemetry') }}

),

prices AS (

    SELECT
        COMMODITY,
        MARKET,
        PRICE_PER_KG,
        QUALITY_PREMIUM
    FROM {{ source('raw', 'COMMODITY_PRICES') }}

),

routes AS (

    SELECT
        ORIGIN,
        MARKET,
        DISTANCE_KM,
        TRAVEL_TIME_HOURS
    FROM {{ source('raw', 'ROUTE_DISTANCES') }}

),

joined_data AS (

    SELECT
        s.CONTAINER_ID,
        s.COMMODITY,
        s.ORIGIN,
        s.DESTINATION,
        s.TEMPERATURE_C,
        s.HUMIDITY_PCT,
        s.VIBRATION_G,
        s.EVENT_TIMESTAMP,
        s.ENVIRONMENTAL_RISK,

        p.MARKET,
        p.PRICE_PER_KG,
        p.QUALITY_PREMIUM,

        r.DISTANCE_KM,
        r.TRAVEL_TIME_HOURS

    FROM sensor_data s

    LEFT JOIN prices p
        ON s.COMMODITY = p.COMMODITY
        AND s.DESTINATION = p.MARKET

    LEFT JOIN routes r
        ON s.ORIGIN = r.ORIGIN
        AND s.DESTINATION = r.MARKET

),

calculated AS (

    SELECT
        *,
        
        CASE
            WHEN TEMPERATURE_C > 15 OR HUMIDITY_PCT > 95 THEN 8
            WHEN TEMPERATURE_C > 12 OR HUMIDITY_PCT > 90 THEN 16
            WHEN TEMPERATURE_C > 10 OR HUMIDITY_PCT > 85 THEN 24
            ELSE 48
        END AS TIME_TO_SPOILAGE_HOURS

    FROM joined_data

)

SELECT
    *,
    
    CASE
        WHEN TIME_TO_SPOILAGE_HOURS <= TRAVEL_TIME_HOURS
            THEN 'AT RISK'
        WHEN ENVIRONMENTAL_RISK = 'HIGH'
            THEN 'WARNING'
        ELSE 'SAFE'
    END AS CONTAINER_STATUS,

    ROUND(
        CASE
            WHEN TIME_TO_SPOILAGE_HOURS <= TRAVEL_TIME_HOURS
                AND QUALITY_PREMIUM > 1
            THEN PRICE_PER_KG * (QUALITY_PREMIUM - 1)
            ELSE 0
        END,
        2
    ) AS SPOILAGE_ARBITRAGE_VALUE

FROM calculated