from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.bash import BashOperator
import pendulum
import pandas as pd
from sqlalchemy import create_engine

# 설정
DBT_PROJECT_DIR = "/opt/airflow/dbt"
DATA_FILE_PATH = "/opt/airflow/data/patient_treatment.csv"
POSTGRES_CONN_ID = "de_project_postgres"

@dag(
    dag_id="elt_patient_pipeline",
    start_date=pendulum.datetime(2023, 1, 1, tz="Asia/Seoul"),
    schedule=None,
    catchup=False,
)
def elt_patient_pipeline():

    @task
    def load_csv_to_postgres():
        # 1. CSV 파일 읽기
        df = pd.read_csv(DATA_FILE_PATH, header=0)
        
        # 2. Hook 생성
        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID, database="analytics_db")
        
        # 3. 스키마 생성 및 테이블 삭제
        hook.run("CREATE SCHEMA IF NOT EXISTS raw;")
        hook.run("DROP TABLE IF EXISTS raw.raw_patient_events CASCADE;")

        # 4. [수정] 연결 정보 수동 조립 (가장 안전한 방법)
        # hook.get_uri() 대신, 연결 정보를 직접 꺼내서 깨끗한 URL을 만듭니다.
        # 이렇게 하면 '__extra__' 같은 잡동사니가 절대 끼어들 수 없습니다.
        conn = hook.get_connection(POSTGRES_CONN_ID)
        db_uri = f"postgresql://{conn.login}:{conn.password}@{conn.host}:{conn.port}/analytics_db"
        
        engine = create_engine(db_uri)

        # 5. 데이터 적재
        df.to_sql(
            name="raw_patient_events",
            con=engine,
            schema="raw",
            if_exists="append",
            index=False
        )
        print(f"Successfully loaded {len(df)} rows to raw.raw_patient_events")

    # [T] dbt 실행
    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command=f"cd {DBT_PROJECT_DIR} && /opt/dbt_venv/bin/dbt run"
    )

    load_csv_to_postgres() >> run_dbt

elt_patient_pipeline()