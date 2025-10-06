# 🚖 NYC Taxi Lakehouse — End-to-End Data Engineering Project

### *(Docker • Airflow • Spark • Delta Lake • MinIO • Trino • Power BI)*

---

## Overview

This project implements a **modern Lakehouse architecture** based on the **Medallion pattern** — enabling data engineers to build an end-to-end data pipeline with **ACID Delta tables**, **distributed Spark jobs**, **S3-compatible object storage (MinIO)**, and **SQL analytics via Trino**.

The orchestration is managed by **Apache Airflow**, while **Power BI** provides interactive dashboards over the final *Gold* analytics layer.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Orchestration Layer                       │
│     Apache Airflow  →  Schedules & monitors ETL pipelines    │
├─────────────────────────────────────────────────────────────┤
│                     Compute Layer                            │
│     Apache Spark  →  Executes ETL jobs (Bronze → Silver → Gold)
├─────────────────────────────────────────────────────────────┤
│                      Storage Layer                           │
│     MinIO (S3)     →  Object store for all Delta tables      │
│     Delta Lake     →  ACID & versioned table format          │
│     Hive Metastore →  Central schema catalog for Spark/Trino │
├─────────────────────────────────────────────────────────────┤
│                      Query & Visualization                   │
│     Trino          →  Unified SQL engine (reads Delta/Parquet)
│     Power BI       →  Dashboard on Gold layer KPIs           │
└─────────────────────────────────────────────────────────────┘
```

---

## Technologies

| Layer                | Tool                                               | Purpose                              |
| :------------------- | :------------------------------------------------- | :----------------------------------- |
| **Orchestration**    | [Apache Airflow](https://airflow.apache.org/)      | DAG scheduling & pipeline monitoring |
| **Processing**       | [Apache Spark](https://spark.apache.org/)          | Distributed data transformation      |
| **Storage**          | [MinIO](https://min.io/)                           | S3-compatible object storage         |
| **Table Format**     | [Delta Lake](https://delta.io/)                    | ACID tables & time travel            |
| **Metadata**         | Hive Metastore                                     | Shared catalog between Spark & Trino |
| **SQL Engine**       | [Trino](https://trino.io/)                         | Query Delta tables via SQL           |
| **Visualization**    | [Power BI](https://powerbi.microsoft.com/)         | BI dashboards                        |
| **Containerization** | [Docker Compose](https://docs.docker.com/compose/) | Local deployment environment         |

---

## Medallion Data Pipeline

| Layer         | Description                                   | Example Path                      |
| ------------- | --------------------------------------------- | --------------------------------- |
| 🥉 **Bronze** | Raw data ingestion (CSV/Parquet)              | `s3a://lake/bronze/trips`         |
| 🥈 **Silver** | Cleaned & standardized data (schema enforced) | `s3a://lake/silver/trips_cleaned` |
| 🥇 **Gold**   | Aggregated metrics & business-ready tables    | `s3a://lake/gold/trips_metrics`   |

**Flow:**

```
Raw → Bronze → Silver → Gold → Power BI
```

---

## Project Structure

```
nyc-taxi-lakehouse/
│
├── dags/                     # Airflow DAGs
│   └── nyc_taxi_lakehouse.py
│
├── jobs/                     # PySpark ETL jobs
│   ├── 01_bronze_ingest.py
│   ├── 02_silver_transform.py
│   └── 03_gold_agg.py
│
├── trino/
│   └── catalog/
│       ├── delta.properties
│       └── hive.properties
│
├── docker-compose.yml         # All services
├── spark-defaults.conf
└── README.md
```

---

## Docker Compose Environment

### Services

| Service          | Description                | Port        |
| ---------------- | -------------------------- | ----------- |
| `spark-master`   | Spark Master node          | 7077 / 8080 |
| `spark-worker`   | Spark executors            | —           |
| `minio`          | Object store               | 9000 / 9001 |
| `hive-metastore` | Central catalog            | 9083        |
| `airflow`        | Orchestrator UI            | 8088        |
| `trino`          | SQL query engine           | 8080        |
| `postgres`       | DB for Airflow & Metastore | —           |

---

## Getting Started

### 1️ Clone Repository

```bash
git clone https://github.com/<your-username>/nyc-taxi-lakehouse.git
cd nyc-taxi-lakehouse
```

### 2️ Start the Stack

```bash
docker compose up -d --build
```

### 3️ Access Web UIs

| Service       | URL                                            | Default Credentials  |
| ------------- | ---------------------------------------------- | -------------------- |
| Airflow       | [http://localhost:8088](http://localhost:8088) | `admin / admin`      |
| Spark UI      | [http://localhost:8080](http://localhost:8080) | —                    |
| MinIO Console | [http://localhost:9001](http://localhost:9001) | `minio / minio12345` |
| Trino Console | [http://localhost:8080](http://localhost:8080) | SQL UI               |
| Power BI      | Connect via ODBC/JDBC → `localhost:8080`       | —                    |

---

## Running the Pipeline

### Step 1: Raw Data → Bronze

```bash
/opt/bitnami/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /opt/jobs/01_bronze_ingest.py
```

### Step 2: Bronze → Silver

```bash
spark-submit /opt/jobs/02_silver_transform.py
```

### Step 3: Silver → Gold

```bash
spark-submit /opt/jobs/03_gold_agg.py
```

> ✅ Airflow DAG `nyc_taxi_lakehouse` automates these steps sequentially.

---

## Trino Catalog Configuration

### `trino/catalog/delta.properties`

```ini
connector.name=delta-lake
hive.metastore.uri=thrift://hive-metastore:9083
fs.native-s3.enabled=true
s3.endpoint=http://minio:9000
s3.path-style-access=true
s3.aws-access-key=minio
s3.aws-secret-key=minio12345
```

### `trino/catalog/hive.properties`

```ini
connector.name=hive
hive.metastore.uri=thrift://hive-metastore:9083
fs.native-s3.enabled=true
s3.endpoint=http://minio:9000
s3.path-style-access=true
s3.aws-access-key=minio
s3.aws-secret-key=minio12345
```

---

## Airflow DAG Example

`dags/nyc_taxi_lakehouse.py`

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

default_args = {"owner": "data", "retries": 1}

spark_submit = "/opt/bitnami/spark/bin/spark-submit --master spark://spark-master:7077 " \
               "--packages io.delta:delta-spark_2.12:3.2.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 " \
               "--conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension " \
               "--conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog " \
               "--conf spark.hadoop.fs.s3a.endpoint=http://minio:9000 " \
               "--conf spark.hadoop.fs.s3a.access.key=minio " \
               "--conf spark.hadoop.fs.s3a.secret.key=minio12345 " \
               "--conf spark.hadoop.fs.s3a.path.style.access=true " \
               "--conf spark.hadoop.fs.s3a.connection.ssl.enabled=false "

with DAG("nyc_taxi_lakehouse",
         default_args=default_args,
         schedule_interval=None,
         start_date=days_ago(1),
         catchup=False) as dag:

    bronze = BashOperator(
        task_id="bronze_ingest",
        bash_command=spark_submit + "/opt/jobs/01_bronze_ingest.py"
    )

    silver = BashOperator(
        task_id="silver_transform",
        bash_command=spark_submit + "/opt/jobs/02_silver_transform.py"
    )

    gold = BashOperator(
        task_id="gold_aggregate",
        bash_command=spark_submit + "/opt/jobs/03_gold_agg.py"
    )

    bronze >> silver >> gold
```

---

## Querying Data via Trino

You can explore Delta tables directly from Trino’s CLI or Power BI:

```sql
SHOW SCHEMAS IN delta;
SHOW TABLES IN delta.nyc;

SELECT pickup_date,
       total_trips,
       avg_fare_amount,
       avg_trip_distance,
       total_revenue
FROM delta.nyc.trips_metrics
ORDER BY pickup_date;
```

---

## Connecting Power BI to Trino

1. Install the **Trino ODBC Driver**
   → [Trino ODBC Download](https://trino.io/download.html)

2. Create a **DSN (Data Source Name)**

   * Host: `localhost`
   * Port: `8080`
   * Catalog: `delta`
   * Schema: `nyc`
   * Auth: none (local setup)

3. In Power BI:

   * **Get Data → ODBC → Trino**
   * Choose `delta.nyc.trips_metrics`
   * Use **DirectQuery** or **Import** mode

---

## 📈 Example Gold Metrics Table

| Column              | Description           |
| ------------------- | --------------------- |
| `pickup_date`       | Aggregation date      |
| `total_trips`       | Total number of trips |
| `avg_fare_amount`   | Average fare          |
| `avg_trip_distance` | Average distance      |
| `total_revenue`     | Total revenue per day |

---

## Future Improvements

* [ ] Add **Grafana** dashboards for monitoring
* [ ] Implement **CI/CD** with GitHub Actions
* [ ] Deploy on **AWS (S3 + EMR + MWAA)**
* [ ] Integrate **Great Expectations** for data validation
* [ ] Use **Airflow Sensors** for data arrival checks

---

## Author

**Samir **
*Data Engineer | Spark & Cloud Enthusiast*
---

## Keywords
`Apache Spark` • `Delta Lake` • `MinIO` • `Airflow` • `Trino` • `Power BI` • `Docker` • `ETL` • `Data Lakehouse`

---
