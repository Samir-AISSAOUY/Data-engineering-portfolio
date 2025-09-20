from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name, current_timestamp
import os, glob

S3_BUCKET = os.getenv("S3_BUCKET", "lake")
RAW_LOCAL = "/opt/data/raw"
BRONZE = f"s3a://{S3_BUCKET}/bronze/trips"

spark = SparkSession.builder.appName("bronze_ingest").getOrCreate()

# Read CSV (including .gz) and parquet if present
df_list = []
csv_files = glob.glob(f"{RAW_LOCAL}/*.csv") + glob.glob(f"{RAW_LOCAL}/*.csv.gz")
parquet_files = glob.glob(f"{RAW_LOCAL}/*.parquet")
if csv_files:
    df_list.append(spark.read.option("header", True).csv(csv_files))
if parquet_files:
    df_list.append(spark.read.parquet(parquet_files))

if not df_list:
    raise SystemExit("No input files found in data/raw")

from functools import reduce
from pyspark.sql import DataFrame as SDF
df = reduce(lambda a,b: a.unionByName(b, allowMissingColumns=True), df_list) if len(df_list)>1 else df_list[0]

df = df.withColumn("_ingest_file", input_file_name()).withColumn("_ingest_ts", current_timestamp())

df.write.format("delta").mode("append").save(BRONZE)

# Optional: add a basic positive fare constraint
spark.sql(f"""CREATE TABLE IF NOT EXISTS bronze_trips
USING DELTA LOCATION '{BRONZE}'
""")
try:
    spark.sql("ALTER TABLE bronze_trips ADD CONSTRAINT positive_fare CHECK (fare_amount >= 0)")
except Exception:
    pass

# metrics
from _utils_metrics import write_metric
write_metric("01_bronze_ingest", BRONZE, df.count())
print(f"Bronze written to {BRONZE}")
