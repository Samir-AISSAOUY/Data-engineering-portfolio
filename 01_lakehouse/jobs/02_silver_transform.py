from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, to_date, when, hour, dayofweek, expr
import os

S3_BUCKET = os.getenv("S3_BUCKET", "lake")
BRONZE = f"s3a://{S3_BUCKET}/bronze/trips"
SILVER = f"s3a://{S3_BUCKET}/silver/trips_cleaned"

spark = SparkSession.builder.appName("silver_transform").getOrCreate()

bronze = spark.read.format("delta").load(BRONZE)

# NYC TLC canonical columns if present
silver = (
    bronze
    .withColumn("pickup_ts", to_timestamp(col("tpep_pickup_datetime")))
    .withColumn("dropoff_ts", to_timestamp(col("tpep_dropoff_datetime")))
    .withColumn("passenger_count", col("passenger_count").cast("int"))
    .withColumn("trip_distance", col("trip_distance").cast("double"))
    .withColumn("fare_amount", col("fare_amount").cast("double"))
    .withColumn("PULocationID", col("PULocationID").cast("int"))
    .withColumn("DOLocationID", col("DOLocationID").cast("int"))
)

# Enrich: duration, speed, tip_rate, date parts
silver = (
    silver
    .withColumn("duration_min", (col("dropoff_ts").cast("long") - col("pickup_ts").cast("long"))/60.0)
    .withColumn("avg_speed_kmh", when(col("trip_distance") > 0, (col("trip_distance")/(col("duration_min")/60.0))).otherwise(None))
    .withColumn("tip_amount", col("tip_amount").cast("double"))
    .withColumn("total_amount", col("total_amount").cast("double"))
    .withColumn("tip_rate", when(col("total_amount") > 0, col("tip_amount")/col("total_amount")).otherwise(None))
    .withColumn("pickup_date", to_date(col("pickup_ts")))
    .withColumn("pickup_hour", hour(col("pickup_ts")))
    .withColumn("pickup_dow", dayofweek(col("pickup_ts")))
)

# Basic quality filters
silver = silver.where(
    (col("pickup_ts").isNotNull()) &
    (col("dropoff_ts").isNotNull()) &
    (col("duration_min") > 0) &
    (col("duration_min") < 720) &  # less than 12h
    (col("trip_distance") >= 0) &
    (col("fare_amount") >= 0)
)

# (Optional) join lookup if file exists
lookup_path = "/opt/data/raw/taxi_zone_lookup.csv"
try:
    lookup = spark.read.option("header", True).csv(lookup_path)        .withColumn("LocationID", col("LocationID").cast("int"))        .select("LocationID","Borough","Zone")
    silver = (silver
        .join(lookup.withColumnRenamed("LocationID","PULocationID"), on="PULocationID", how="left")
        .withColumnRenamed("Borough","PU_Borough").withColumnRenamed("Zone","PU_Zone")
        .join(lookup.withColumnRenamed("LocationID","DOLocationID"), on="DOLocationID", how="left", suffixes=("_pu","_do"))
        .withColumnRenamed("Borough","DO_Borough").withColumnRenamed("Zone","DO_Zone")
    )
except Exception:
    pass

# Write partitioned by date
silver.write.format("delta").mode("overwrite").option("overwriteSchema","true").partitionBy("pickup_date").save(SILVER)

# metrics
from _utils_metrics import write_metric
write_metric("02_silver_transform", SILVER, silver.count())
print(f"Silver written to {SILVER}")
