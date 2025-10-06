```markdown
# 🚖 NYC Taxi Lakehouse — End-to-End Data Engineering Project

### *(Docker • Airflow • Spark • Delta Lake • MinIO • Trino • Power BI)*

---

## 🚀 Introduction

**NYC Taxi Lakehouse** est un projet de bout en bout démontrant la mise en place d’une **architecture Data Lakehouse moderne** à partir des données publiques **NYC Taxi Trips**.

L’objectif est de construire une plateforme **scalable**, **fiable** et **analytique-ready**, simulant un environnement cloud local avec :
- stockage objet S3 (via MinIO),
- tables ACID Delta Lake,
- orchestration Airflow,
- traitement distribué Spark,
- exploration SQL avec Trino,
- visualisation Power BI.

> 🧭 *Cas d’usage métier : analyser le trafic taxi à New York — volume de trajets, revenus, distances moyennes et tendances temporelles.*

---

## 🧠 Architecture Conceptuelle

Le pipeline suit le **Medallion Pattern** :  
Raw → Bronze → Silver → Gold → Power BI

```

Airflow ─► Spark ─► Delta Lake (MinIO S3)
│
▼
Trino / Power BI

```

### 🥇 Méthodologie

| Layer | Description | Exemple de traitement |
|-------|--------------|----------------------|
| 🥉 **Bronze** | Données brutes ingérées depuis les fichiers Parquet/CSV | Ingestion simple & stockage Delta |
| 🥈 **Silver** | Données nettoyées, typées et enrichies | Standardisation des schémas, suppression des nulls |
| 🥇 **Gold** | Tables métiers prêtes à l’analyse | Calcul d’agrégats et KPIs quotidiens |

---

## ⚙️ Architecture Technique

| Couche | Outil | Rôle / Valeur ajoutée |
| :------ | :----- | :------------------ |
| **Orchestration** | [Apache Airflow](https://airflow.apache.org/) | Gestion des dépendances et planification des ETL |
| **Traitement distribué** | [Apache Spark](https://spark.apache.org/) | Transformation et agrégation des données à grande échelle |
| **Format de table** | [Delta Lake](https://delta.io/) | Transactions ACID, versioning et time travel |
| **Stockage objet** | [MinIO](https://min.io/) | S3-compatible pour environnement cloud-like |
| **Catalogue** | Hive Metastore | Schéma partagé entre Spark et Trino |
| **SQL Engine** | [Trino](https://trino.io/) | Requêtes SQL unifiées sur Delta Lake |
| **BI / Visualisation** | [Power BI](https://powerbi.microsoft.com/) | Tableau de bord analytique |
| **Infra** | [Docker Compose](https://docs.docker.com/compose/) | Déploiement local reproductible |

---

## 📥 Data Sources

Le projet s’appuie sur les données publiques de la **NYC Taxi & Limousine Commission (TLC)**.  
Elles contiennent l’ensemble des courses de taxis jaunes à New York, leurs tarifs, distances et zones géographiques.

### 🗂️ Données utilisées

| Fichier | Description | Format | Source |
|----------|--------------|---------|---------|
| `yellow_tripdata_2023-01.parquet` → `yellow_tripdata_2023-06.parquet` | Courses de taxi (janvier à juin 2023) | Parquet | [TLC Trip Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) |
| `taxi_zone_lookup.csv` | Référentiel des zones géographiques | CSV | [TLC Zone Lookup](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) |

### 📂 Structure locale

```

data/
├── raw/
│   ├── yellow_tripdata_2023-01.parquet
│   ├── yellow_tripdata_2023-02.parquet
│   ├── ...
│   └── taxi_zone_lookup.csv
├── bronze/
├── silver/
└── gold/

````

> Les fichiers bruts sont ingérés depuis `data/raw/` vers le bucket MinIO (`s3a://lake/bronze/`).

### 📜 Téléchargement (Windows CMD)

```bash
cd C:\Users\Samir SC\Desktop\Lakehouse_projet\01_lakehouse\data\raw

:: Télécharger les 6 premiers mois de 2023
for %m in (01 02 03 04 05 06) do (
    curl -L -o yellow_tripdata_2023-%m.parquet https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-%m.parquet
)

:: Référentiel des zones
curl -L -o taxi_zone_lookup.csv https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
````

### 🌍 Colonnes principales

| Colonne                        | Type      | Description                          |
| ------------------------------ | --------- | ------------------------------------ |
| `tpep_pickup_datetime`         | Timestamp | Heure de départ                      |
| `tpep_dropoff_datetime`        | Timestamp | Heure d’arrivée                      |
| `passenger_count`              | Int       | Nombre de passagers                  |
| `trip_distance`                | Float     | Distance parcourue (miles)           |
| `fare_amount`                  | Float     | Montant de la course                 |
| `tip_amount`                   | Float     | Pourboire                            |
| `total_amount`                 | Float     | Montant total payé                   |
| `PULocationID`, `DOLocationID` | Int       | Zones géographiques (pickup/dropoff) |

---

## 📦 Structure du Projet

```
nyc-taxi-lakehouse/
├── dags/                   # DAGs Airflow (Bronze → Silver → Gold)
├── jobs/                   # Scripts PySpark d’ingestion et de transformation
│   ├── 01_bronze_ingest.py
│   ├── 02_silver_transform.py
│   └── 03_gold_agg.py
├── trino/catalog/           # Configurations Delta & Hive
├── data/                    # Données locales (raw, bronze, silver, gold)
├── docker-compose.yml        # Stack complète
└── README.md
```

---

## 🧩 Fonctionnalités Clés

* ✅ Orchestration complète du pipeline via Airflow
* ✅ Tables Delta Lake ACID avec *time travel*
* ✅ Stockage objet S3 local (MinIO)
* ✅ Exploration SQL avec Trino
* ✅ Visualisation Power BI connectée au Gold Layer
* ✅ Compatible Cloud AWS (S3, EMR, MWAA)

---

## 🧱 Déploiement Local

### 1️⃣ Cloner le projet

```bash
git clone https://github.com/<your-username>/nyc-taxi-lakehouse.git
cd nyc-taxi-lakehouse
```

### 2️⃣ Démarrer l’environnement

```bash
docker compose up -d --build
```

### 3️⃣ Accéder aux interfaces

| Service           | URL                                            | Identifiants         |
| ----------------- | ---------------------------------------------- | -------------------- |
| **Airflow**       | [http://localhost:8088](http://localhost:8088) | `admin / admin`      |
| **Spark UI**      | [http://localhost:4040](http://localhost:4040) | —                    |
| **MinIO Console** | [http://localhost:9001](http://localhost:9001) | `minio / minio12345` |
| **Trino UI**      | [http://localhost:8080](http://localhost:8080) | —                    |

---

## ⚡ Exécution du Pipeline

### Étapes manuelles

```bash
spark-submit /opt/jobs/01_bronze_ingest.py
spark-submit /opt/jobs/02_silver_transform.py
spark-submit /opt/jobs/03_gold_agg.py
```

### Ou via Airflow DAG

Le DAG `nyc_taxi_lakehouse` orchestre automatiquement :

```
Bronze → Silver → Gold
```

---

## 🧮 Exemple de Requête Trino

```sql
SELECT pickup_date,
       total_trips,
       avg_fare_amount,
       avg_trip_distance,
       total_revenue
FROM delta.nyc.trips_metrics
ORDER BY pickup_date DESC;
```

---

## 📊 Dashboard Power BI

Le tableau de bord Power BI se connecte à Trino (catalogue `delta`) et permet de :

* Suivre le volume quotidien de trajets
* Visualiser les revenus et distances moyennes
* Identifier les heures de pointe et tendances mensuelles
* Explorer les performances par zone géographique

> *(Ajoutez ici une capture d’écran Power BI — très valorisant pour ton portfolio !)*

---

## 🔧 Améliorations Futures

* [ ] Data Quality Checks avec **Great Expectations**
* [ ] Monitoring via **Grafana + Prometheus**
* [ ] Lignée de données avec **OpenLineage**
* [ ] Intégration CI/CD (**GitHub Actions**)
* [ ] Déploiement Cloud (AWS S3 + EMR + MWAA)

---

## 👨‍💻 Auteur

**Samir**
*Data Engineer | Spark & Cloud Enthusiast*

---

## 🧩 Compétences démontrées

> ✅ Orchestration (Airflow)
> ✅ Distributed ETL (Spark + Delta Lake)
> ✅ Data Modeling (Bronze/Silver/Gold)
> ✅ SQL Analytics (Trino, Power BI)
> ✅ Object Storage (MinIO / S3)
> ✅ DevOps (Docker Compose, Environment Management)

---

## 🏁 Keywords

`Apache Spark` • `Delta Lake` • `MinIO` • `Airflow` • `Trino` • `Power BI` • `Docker` • `ETL` • `Data Lakehouse` • `Data Engineering`

```
