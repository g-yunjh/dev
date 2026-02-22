import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = (
    SparkSession.builder.appName("Patient_Data_Loader")
    .config("spark.jars.packages", "org.postgresql:postgresql:42.6.0")
    .getOrCreate()
)

csv_file_path = "/opt/spark/work-dir/data/patient_treatment.csv"

# 🌟 [수정] DB 주소도 서비스 이름(postgres)으로 변경
db_url = "jdbc:postgresql://de_project_postgres:5432/analytics_db"
db_properties = {
    "user": "airflow",
    "password": "airflow",
    "driver": "org.postgresql.Driver"
}
target_table = "raw.raw_patient_events"

print(f"--- Starting Spark Job: Loading {csv_file_path} ---")

try:
    df = spark.read.csv(csv_file_path, header=True, inferSchema=True)

    df_transformed = df.select(
        col("Patient").alias("patient"),
        col(" action").alias(" action"),
        col(" org:resource").alias(" org:resource"),
        col(" DateTime").alias(" DateTime")
    )

    df_transformed.write.mode("overwrite") \
        .jdbc(url=db_url, table=target_table, properties=db_properties)
    
    print("--- Spark Job Completed Successfully ---")

except Exception as e:
    print(f"!!! Error: {e}")
    sys.exit(1)
finally:
    spark.stop()