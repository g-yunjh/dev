from airflow.decorators import dag
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.bash import BashOperator
import pendulum

SPARK_CONN_ID = "spark_default"
SPARK_JOB_FILE = "/opt/airflow/scripts/spark_load_patients.py"
POSTGRES_CONN_ID = "de_project_postgres"

@dag(
    dag_id="elt_spark_pipeline",
    start_date=pendulum.datetime(2023, 1, 1, tz="Asia/Seoul"),
    schedule=None,
    catchup=False,
)
def elt_spark_pipeline():

    # 🌟 [추가] Spark 실행 전 테이블 정리 (CASCADE)
    clean_up_table = PostgresOperator(
        task_id="clean_up_table",
        postgres_conn_id=POSTGRES_CONN_ID,
        sql="DROP TABLE IF EXISTS raw.raw_patient_events CASCADE;"
    )

    # [Task 1] Spark 작업 (이제 overwrite 실패 안 함)
    load_csv_with_spark = SparkSubmitOperator(
        task_id="load_csv_with_spark",
        conn_id=SPARK_CONN_ID,
        application=SPARK_JOB_FILE,
        verbose=True,
        packages="org.postgresql:postgresql:42.6.0",
        conf={
            "spark.master": "spark://spark-master:7077",
            "spark.submit.deployMode": "client",
            "spark.driver.host": "airflow-scheduler",
            "spark.driver.bindAddress": "0.0.0.0",
            # 파이썬 경로 강제 지정 (혹시 모르니 유지)
            "spark.pyspark.python": "/usr/bin/python3",
            "spark.pyspark.driver.python": "/usr/local/bin/python"
        }
    )

    # [Task 2] dbt 실행
    run_dbt = BashOperator(
        task_id="run_dbt_after_spark",
        bash_command="cd /opt/airflow/dbt && /opt/dbt_venv/bin/dbt run"
    )

    # 순서: 청소 -> 적재 -> 변환
    clean_up_table >> load_csv_with_spark >> run_dbt

elt_spark_pipeline()