import time
import json
import pandas as pd
from kafka import KafkaProducer

# 1. Kafka Producer 설정
# docker-compose 네트워크 안에서는 'kafka' 호스트명을 씁니다.
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

TOPIC_NAME = "patient_events"
CSV_FILE = "/opt/airflow/data/patient_treatment.csv"

print(f">>> Starting to produce events to topic '{TOPIC_NAME}'...")

# 2. CSV 읽기 및 전송
try:
    df = pd.read_csv(CSV_FILE)
    
    # 🌟 [수정 1] 컬럼명 앞뒤 공백 제거 (예: " action" -> "action")
    df.columns = df.columns.str.strip()
    
    # 디버깅: 실제 컬럼명 확인
    print(f">>> Columns found: {df.columns.tolist()}")

    for index, row in df.iterrows():
        event = row.to_dict()
        producer.send(TOPIC_NAME, value=event)
        
        # 🌟 [수정 2] 대소문자/공백 이슈 방지를 위해 .get() 사용
        # 실제 컬럼명은 'patient' (소문자) 일 확률이 높음
        p_id = event.get('patient') or event.get('Patient') or "Unknown"
        action = event.get('action') or event.get(' action') or "Unknown"
        
        print(f"Sent: {p_id} - {action}")
        
        time.sleep(1)

except Exception as e:
    print(f"Error: {e}")
finally:
    producer.close()