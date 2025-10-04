````markdown
# 🚖 NYC Taxi Lakehouse Project  
### A Complete End-to-End Data Engineering Pipeline with PySpark, Delta Lake, and MinIO
---

## Overview
This project builds a **modern Lakehouse architecture** using **Apache Spark**, **Delta Lake**, and **MinIO (S3-compatible object store)**, deployed in **Docker containers**.

We process **NYC Taxi trips data** (6 months of parquet & CSV files), applying transformations through **Bronze → Silver → Gold** layers following the **Medallion Architecture** pattern.

---

## Architecture Overview

The full environment is containerized with Docker Compose:

- **Spark Master & Workers** – distributed processing with PySpark  
- **MinIO** – S3-compatible data lake storage  
- **Delta Lake** – transaction layer for data versioning & ACID  
- **Visual Studio code ** – for exploration and analysis  

📸 *Architecture Diagram:*  
![Lakehouse Architecture](images/lakehouse_architecture.png)

---

## 🔁 Medallion Data Pipeline

The project follows the **three-layer Medallion Architecture**:

| Layer | Description | Output Example |
|-------|--------------|----------------|
| **Bronze** | Raw ingestion layer – load data “as-is” from source into Delta tables | `s3a://lake/bronze/trips` |
| **Silver** | Cleaned & standardized data with proper schema and null handling | `s3a://lake/silver/trips_cleaned` |
| **Gold** | Aggregated & business-ready analytics tables | `s3a://lake/gold/trips_metrics` |

📸 *Medallion Layers:*  
![Medallion Architecture](images/medallion_layers.png)

---

## ⚙️ Data Flow

1. **Raw Data Ingestion (Bronze)**
   - Loads raw `.csv` and `.parquet` files
   - Adds metadata columns (`_ingest_file`, `_ingest_ts`)

2. **Transformation & Cleaning (Silver)**
   - Cleans nulls, fixes schema, rounds numeric columns
   - Removes duplicates

3. **Aggregation (Gold)**
   - Aggregates by day/hour/location
   - Computes KPIs: total trips, avg fare, avg distance, total revenue

📸 *Data Flow Diagram:*  
![Data Flow](images/data_flow.png)

---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| **Data Processing** | Apache Spark (PySpark) |
| **Storage Layer** | Delta Lake |
| **Data Lake** | MinIO (S3-compatible) |
| **Containerization** | Docker & Docker Compose |
| **Scripting** | Python |
| **Visualization (optional)** | Jupyter Notebooks |

---

## 🚀 How to Run the Project

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/nyc-taxi-lakehouse.git
cd nyc-taxi-lakehouse/01_lakehouse
````

### 2️⃣ Start all services

```bash
docker compose up -d --build
```

### 3️⃣ Access MinIO

* **URL:** [http://localhost:9001](http://localhost:9001)
* **Username:** `minio`
* **Password:** `minio12345`

### 4️⃣ Open a Spark Worker shell

```bash
docker compose exec -it spark-worker bash
```

### 5️⃣ Run each ETL job sequentially

```bash
# Bronze
/opt/bitnami/spark/bin/spark-submit --master spark://spark-master:7077 \
  --packages io.delta:delta-spark_2.12:3.2.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
  --conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
  --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog \
  --conf spark.hadoop.fs.s3a.endpoint=http://minio:9000 \
  --conf spark.hadoop.fs.s3a.access.key=minio \
  --conf spark.hadoop.fs.s3a.secret.key=minio12345 \
  --conf spark.hadoop.fs.s3a.path.style.access=true \
  --conf spark.hadoop.fs.s3a.connection.ssl.enabled=false \
  /opt/jobs/01_bronze_ingest.py
```

Then:

```bash
/opt/bitnami/spark/bin/spark-submit ... /opt/jobs/02_silver_transform.py
/opt/bitnami/spark/bin/spark-submit ... /opt/jobs/03_gold_agg.py
```

---

## ✅ Verifying Each Layer

### Check row counts in Spark SQL:

```bash
/opt/bitnami/spark/bin/spark-sql \
  --master spark://spark-master:7077 \
  --packages io.delta:delta-spark_2.12:3.2.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
  -e "SELECT COUNT(*) AS bronze_rows FROM delta.\`s3a://lake/bronze/trips\`;"
```

Repeat for:

* `s3a://lake/silver/trips_cleaned`
* `s3a://lake/gold/trips_metrics`

Or check visually in **MinIO → Buckets → lake → bronze/silver/gold**

---

## 📈 Example Results

| Layer  | Table                 | Row Count | Description              |
| ------ | --------------------- | --------- | ------------------------ |
| Bronze | `trips`               | ~19M      | Raw taxi trip data       |
| Silver | `trips_cleaned`       | ~18M      | Cleaned & validated      |
| Gold   | `trip_metrics_by_day` | 31 rows   | Daily aggregated metrics |

---

## 🌟 Future Improvements

* Integrate **Airflow** or **Dagster** for orchestration
* Add **Grafana dashboards** for Gold layer metrics
* Deploy on **AWS S3 & EMR** for scalability
* Add **CI/CD with GitHub Actions**

---

## 👨‍💻 Author

**Samir SC**
Data Engineer | Spark & Cloud Enthusiast
🔗 [LinkedIn](https://linkedin.com) • [GitHub](https://github.com)

---

📦 *Technologies:*
`Apache Spark` • `Delta Lake` • `MinIO` • `Docker` • `PySpark` • `ETL` • `Data Engineering`

```

---

## 🖼️ À propos des images à inclure

Place-les dans un dossier `images/` à la racine du repo :

| Nom du fichier | Description |
|----------------|--------------|
| `lakehouse_architecture.png` | Schéma général (Spark, Docker, MinIO, Delta) |
| `medallion_layers.png` | Représentation Bronze → Silver → Gold |
| `data_flow.png` | Flux de transformation complet |

Je peux te générer ces 3 images **avec un style pro (fond sombre, style cloud, logos inclus)** — veux-tu que je les crée maintenant pour toi ?  
👉 Cela rendra ton README **visuellement impressionnant** et prêt à publier sur GitHub.
```
