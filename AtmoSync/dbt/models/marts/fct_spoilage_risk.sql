WITH telemetry AS (
    SELECT * FROM {{ ref('stg_iot_telemetry') }}
)
SELECT
    container_id,
    commodity,
    origin,
    destination,
    temperature_c,
    humidity_pct,
    vibration_g,
    telemetry_at,
    CASE 
        WHEN temperature_c > 12.0 OR humidity_pct > 85.0 THEN 0.18 -- 18% spoilage rate per hour
        WHEN temperature_c > 8.0 THEN 0.08
        ELSE 0.02
    END AS hourly_spoilage_rate,
    CASE
        WHEN temperature_c > 12.0 OR humidity_pct > 85.0 THEN 'HIGH_RISK'
        WHEN temperature_c > 8.0 THEN 'MEDIUM_RISK'
        ELSE 'OPTIMAL'
    END AS container_health_status
FROM telemetry