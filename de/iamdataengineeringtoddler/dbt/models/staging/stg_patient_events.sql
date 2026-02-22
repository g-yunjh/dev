-- models/staging/stg_patient_events.sql
-- raw.raw_patient_events 테이블로부터 데이터를 읽어 정제합니다.

with source as (

    -- 🌟 'raw_patient_events' 테이블을 'source'로 지정합니다.
    -- 이 테이블은 2.3단계에서 Airflow가 CSV를 읽어 생성할 것입니다.
    select * from {{ source('raw', 'raw_patient_events') }}

),

renamed as (

    select
        "patient" as patient_id,
        " action" as event_name,
        " org:resource" as resource,
        
        -- DateTime 컬럼을 timestamp 타입으로 변환
        " DateTime"::timestamp as event_datetime

    from source

)

select * from renamed
