-- models/marts/mart_patient_summary.sql
-- stg_patient_events 모델을 참조하여 환자별 요약 데이터를 만듭니다.

with patient_events as (
    select * from {{ ref('stg_patient_events') }} -- 🌟 dbt의 ref 함수
)

select
    patient_id,
    count(*) as total_events,
    min(event_datetime) as first_event_datetime,
    max(event_datetime) as last_event_datetime
from
    patient_events
group by
    patient_id