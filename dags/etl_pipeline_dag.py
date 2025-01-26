from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

##other imports
import requests
import psycopg2
import logging
from dotenv import load_dotenv
import os
####get db connections ##

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", 5432),
    "dbname": os.getenv("POSTGRES_DB", "telco_db"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
}

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_db_connection():
    """Connect to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        raise

# Default DAG arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# DAG 1: Extract Data Every 8 Hours
with DAG(
    dag_id="extract_data_dag",
    default_args=default_args,
    description="Extract data every 8 hours",
    schedule_interval="0 */8 * * *",  # Every 8 hours
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
) as extract_dag:

    # Task: Run extract mode of etl_pipeline.py
    extract_data_task = BashOperator(
        task_id="extract_data_task",
        bash_command="python /opt/airflow/dags/utils/etl_pipeline.py extract",
    )

# DAG 2: Full ETL Once Daily at Midnight
with DAG(
    dag_id="etl_pipeline_dag",
    default_args=default_args,
    description="Run full ETL pipeline daily at midnight",
    schedule_interval="0 0 * * *",  # Every day at midnight
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
) as etl_dag:

    # Task: Run full etl_pipeline.py
    full_etl_task = BashOperator(
        task_id="run_full_etl",
        bash_command="python /opt/airflow/dags/utils/etl_pipeline.py",
    )
