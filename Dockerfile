FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    postgresql-client \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

WORKDIR /app

COPY app.py /app/
COPY db_utils.py /app/
COPY wait_db_init.sh /app/wait_db_init.sh
COPY dags/utils/etl_pipeline.py /opt/airflow/dags/utils/etl_pipeline.py
COPY dags/etl_pipeline_dag.py /opt/airflow/dags/etl_pipeline_dag.py
COPY Etl_pipeline_test.py /app/
COPY sql_queries.py /app/

RUN chmod +x /app/wait_db_init.sh

EXPOSE 5001

CMD ["sh", "/app/wait_db_init.sh", "python", "app.py"]


