SHELL := /bin/bash

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

# Download sample dataset (NYC Yellow Taxi 2022-01) + taxi zone lookup
sample:
	mkdir -p data/raw
	curl -L -o data/raw/yellow_tripdata_2022-01.csv.gz https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-01.csv.gz
	gunzip -f data/raw/yellow_tripdata_2022-01.csv.gz
	curl -L -o data/raw/taxi_zone_lookup.csv https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv || true

bronze:
	docker compose exec spark-worker bash -lc "cd /opt && ./spark/submit.sh /opt/jobs/01_bronze_ingest.py"

silver:
	docker compose exec spark-worker bash -lc "cd /opt && ./spark/submit.sh /opt/jobs/02_silver_transform.py"

gold:
	docker compose exec spark-worker bash -lc "cd /opt && ./spark/submit.sh /opt/jobs/03_gold_aggregates.py"

etl: bronze silver gold

gold_export_csv:
	docker compose exec spark-worker bash -lc "python - <<'PY'\nfrom pyspark.sql import SparkSession\nspark=SparkSession.builder.getOrCreate()\nfor p in ['s3a://lake/gold/marts/trip_metrics_by_hour','s3a://lake/gold/marts/trip_metrics_by_zone_hour']:\n df=spark.read.format('delta').load(p)\n out=p.split('/')[-1]\n df.coalesce(1).write.mode('overwrite').option('header','true').csv(f'/opt/data/gold_exports/{out}')\n print('Exported', out)\nPY"

metrics_show:
	docker compose exec spark-worker bash -lc "python - <<'PY'\nfrom pyspark.sql import SparkSession\nspark=SparkSession.builder.getOrCreate()\ndf=spark.read.format('delta').load('s3a://lake/system/metrics')\ndf.orderBy('ts', ascending=False).show(20, False)\nPY"
