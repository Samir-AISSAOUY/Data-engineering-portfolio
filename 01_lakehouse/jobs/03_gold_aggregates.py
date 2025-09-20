from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_trunc, avg, count, sum as _sum, round as _round
import os

S3_BUCKET = os.getenv("S3_BUCKET", "lake")
SILVER = f"s3a://{S3_BUCKET}/silver/trips_cleaned"
GOLD_HOURLY = f"s3a://{S3_BUCKET}/gold/marts/trip_metrics_by_hour"
GOLD_ZONE_HOURLY = f"s3a://{S3_BUCKET}/gold/marts/trip_metrics_by_zone_hour"

spark = SparkSession.builder.appName("gold_aggregates").getOrCreate()

silver = spark.read.format("delta").load(SILVER)

hourly = (
    silver
    .withColumn("hour", date_trunc("hour", col("pickup_ts")))
    .groupBy("hour")
    .agg(
        count("*").alias("trip_count"),
        _round(avg("trip_distance"), 3).alias("avg_distance"),
        _round(avg("fare_amount"), 3).alias("avg_fare"),
        _round(_sum("fare_amount"), 2).alias("total_fares"),
        _round(avg("avg_speed_kmh"), 2).alias("avg_speed_kmh"),
        _round(avg("tip_rate"), 3).alias("avg_tip_rate")
    )
    .orderBy("hour")
)
hourly.write.format("delta").mode("overwrite").option("overwriteSchema","true").save(GOLD_HOURLY)

# By pickup borough (if available) per hour
cols = silver.columns
if "PU_Borough" in cols:
    zone_hourly = (
        silver
        .withColumn("hour", date_trunc("hour", col("pickup_ts")))
        .groupBy("hour","PU_Borough")
        .agg(
            count("*").alias("trip_count"),
            _round(avg("fare_amount"), 3).alias("avg_fare"),
            _round(_sum("fare_amount"), 2).alias("total_fares")
        )
        .orderBy("hour","PU_Borough")
    )
    zone_hourly.write.format("delta").mode("overwrite").option("overwriteSchema","true").save(GOLD_ZONE_HOURLY)

# metrics
from _utils_metrics import write_metric
write_metric("03_gold_aggregates", GOLD_HOURLY, hourly.count())
print(f"Gold written to {GOLD_HOURLY} (+ zone/hour if lookup present)")
