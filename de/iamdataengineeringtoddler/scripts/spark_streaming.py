import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType

# 1. Spark Session 생성
spark = (
    SparkSession.builder
    .appName("Patient_Streaming")
    # Kafka 라이브러리 (Spark 3.5.1 / Scala 2.12)
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1")
    # 로컬 모드 UI 포트 충돌 방지
    .config("spark.ui.port", "4050")
    .getOrCreate()
)

# 로그 레벨 설정
spark.sparkContext.setLogLevel("WARN")

print(">>> Spark Session Created successfully!")

try:
    # 2. Kafka 읽기 설정
    df_raw = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "patient_events") \
        .option("startingOffsets", "latest") \
        .option("failOnDataLoss", "false") \
        .load()

    print(">>> Kafka Stream initialized.")

    # 3. 데이터 파싱
    schema = StructType() \
        .add("patient", StringType()) \
        .add("action", StringType()) \
        .add("org:resource", StringType()) \
        .add("DateTime", StringType()) \
        .add("Patient", StringType()) 

    df_parsed = df_raw.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")

    # 4. 집계 (Action별 카운트)
    df_count = df_parsed.fillna("Unknown", subset=["action"]).groupBy("action").count()

    print(">>> Query Definition Created.")

    # 5. 콘솔 출력 시작
    query = df_count \
        .writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", "false") \
        .option("checkpointLocation", "/tmp/spark-checkpoint") \
        .start()

    print(">>> Streaming is running... (Press Ctrl+C to stop)")
    query.awaitTermination()

except Exception as e:
    print(f"!!! CRITICAL ERROR !!!: {e}")
    sys.exit(1)