from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit
import os

def write_metric(job_name: str, table: str, row_count: int):
    spark = SparkSession.builder.getOrCreate()
    target = f"s3a://{os.getenv('S3_BUCKET','lake')}/system/metrics"
    df = spark.createDataFrame([
        (job_name, table, row_count)
    ], ['job', 'table', 'rows'])    .withColumn('ts', current_timestamp())
    df.write.format('delta').mode('append').save(target)
