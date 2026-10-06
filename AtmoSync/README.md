# AtmoSync: Micro-Climate Arbitrage Analytics

AtmoSync is a streaming ELT analytics pipeline designed to track real-time container telemetry (temperature, humidity, vibration) and calculate "Spoilage Arbitrage" margins to optimize commodity shipment rerouting[cite: 1].

## Pipeline Architecture
- **Streaming Ingestion**: Python IoT Simulator -> Apache Kafka -> Dead-Letter Queue (DLQ)[cite: 1]
- **Data Warehouse**: Snowflake (`ATMOSYNC_DB.RAW.RAW_IOT_DATA`)[cite: 1]
- **Transformation Layer**: dbt Core (`stg_iot_telemetry`, `fct_spoilage_risk`, `fct_spoilage_arbitrage`)[cite: 1, 2]
- **Visualization & Alerts**: Real-time alerts and materialized summary views[cite: 1, 2]

## Project Structure
```text
AtmoSync/
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── src_snowflake.yml
│   │   │   ├── stg_iot_telemetry.sql
│   │   │   └── stg_commodity_prices.sql
│   │   └── marts/
│   │       ├── fct_spoilage_risk.sql
│   │       ├── fct_spoilage_arbitrage.sql
│   │       └── schema.yml
├── kafka/
│   ├── kafka_producer.py
│   ├── snowflake_consumer.py
│   └── alert_notifier.py
├── sql/
│   ├── 01_create_raw_tables.sql
│   └── 02_materialized_views.sql
└── README.md