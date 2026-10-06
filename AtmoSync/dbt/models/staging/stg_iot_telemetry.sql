WITH source AS (
    SELECT * FROM {{ source('raw_data', 'RAW_IOT_DATA') }}
)
SELECT
    UPPER(CONTAINER_ID) AS container_id,
    COMMODITY AS commodity,
    ORIGIN AS origin,
    DESTINATION AS destination,
    ROUND(TEMPERATURE_C, 2) AS temperature_c,
    ROUND(HUMIDITY_PCT, 2) AS humidity_pct,
    ROUND(VIBRATION_G, 3) AS vibration_g,
    EVENT_TIMESTAMP AS telemetry_at,
    INGESTED_AT AS ingested_at
FROM source