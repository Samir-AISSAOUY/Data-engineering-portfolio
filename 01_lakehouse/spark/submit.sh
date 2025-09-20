#!/usr/bin/env bash
set -euo pipefail

DELTA_VERSION=${DELTA_VERSION:-3.2.0}
HADOOP_AWS_VERSION=${HADOOP_AWS_VERSION:-3.3.4}
AWS_SDK_BUNDLE=${AWS_SDK_BUNDLE:-1.12.262}

PACKAGES="io.delta:delta-spark_2.12:${DELTA_VERSION},org.apache.hadoop:hadoop-aws:${HADOOP_AWS_VERSION},com.amazonaws:aws-java-sdk-bundle:${AWS_SDK_BUNDLE}"

/opt/bitnami/spark/bin/spark-submit   --master spark://spark-master:7077   --packages "$PACKAGES"   --conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension   --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog   "$@"
