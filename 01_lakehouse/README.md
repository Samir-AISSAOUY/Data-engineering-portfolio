# Projet 1 — Lakehouse mobilité (Bronze/Silver/Gold)

**100% gratuit & local (Docker).** MinIO (S3) + Spark 3.5 + Delta Lake. Datasets: NYC TLC.

## Lancer en 5 minutes
```bash
cp .env.example .env
make up
make sample
make etl
# UIs: MinIO http://localhost:9001 | Spark Master http://localhost:8080 | Superset http://localhost:8088
```
Export CSV pour la BI:
```bash
make gold_export_csv  # fichiers dans data/gold_exports/
```

## Médaillons
- **Bronze**: ingestion brute → `s3a://lake/bronze/trips`
- **Silver**: nettoyage + enrichissements → `s3a://lake/silver/trips_cleaned` (partitionné par date)
- **Gold**: agrégats analytiques → `s3a://lake/gold/marts/*`
- **System**: métriques d'exécution → `s3a://lake/system/metrics`

## Bullets CV
- Lakehouse en médaillons (**MinIO + Spark/Delta**), tables **Gold** prêtes BI, métriques d’exécution, reproductible via **Docker Compose**.
```

