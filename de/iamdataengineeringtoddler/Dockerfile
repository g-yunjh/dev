FROM apache/airflow:2.9.1-python3.10

USER root

# 1. Java 설치 (Spark용)
RUN apt-get update && \
    apt-get install -y git openjdk-17-jdk-headless && \
    apt-get clean

# 2. JAVA_HOME 설정
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# 3. dbt 가상환경 격리
RUN python3 -m venv /opt/dbt_venv && \
    /opt/dbt_venv/bin/pip install --no-cache-dir "dbt-postgres==1.7.10" && \
    ln -s /opt/dbt_venv/bin/dbt /usr/local/bin/dbt

USER airflow

# 4. 호환성 목록 URL
ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-2.9.1/constraints-3.10.txt"

# 5. 라이브러리 설치 (kafka-python 추가됨)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    "apache-airflow-providers-apache-spark" \
    "apache-airflow-providers-postgres" \
    "pyspark" \
    "kafka-python" \
    --constraint "${CONSTRAINT_URL}"