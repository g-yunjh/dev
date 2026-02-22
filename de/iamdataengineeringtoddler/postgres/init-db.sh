#!/bin/bash
set -e

# analytics_db가 존재하지 않으면 생성하기
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 1 FROM pg_database WHERE datname = 'analytics_db'
    \gexec
    SELECT 'CREATE DATABASE analytics_db'
    WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'analytics_db')
    \gexec
EOSQL
