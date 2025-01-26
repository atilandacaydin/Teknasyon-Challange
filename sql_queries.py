import psycopg2
import csv
import logging
from dotenv import load_dotenv
import os

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


def avg_usage():
    """Find avarage data usage, avg call min and avg sms count"""
    avg_query = """
        SELECT 
            s.customer_id,
            AVG(u.call_minutes::NUMERIC) AS avg_call_minutes,
            AVG(u.data_usage::NUMERIC) AS avg_data_usage,
            AVG(u.sms_count) AS avg_sms_count
        FROM 
            subscriptions s
        JOIN
            usage u
        ON  
            s.subscription_id = u.subscription_id
        GROUP BY
           s.customer_id
        ORDER BY
            s.customer_id;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(avg_query)
        results_query_avg= cur.fetchall()
        cur.close()
        conn.close()
        logging.info("success!")
    except Exception as e:
        logging.error(f"Failed : {e}")
        raise
    
    output_path = os.getenv("CSV_OUTPUT_PATH", "/tmp/avg_query.csv")
    with open(output_path,'w',newline='') as csvfile:
        try:

            writer = csv.writer(csvfile)
            writer.writerows(results_query_avg)
            logging.info(f"Csv success to{output_path}")
        except Exception as e:
            logging.error(f"failed csv : {e}")
            raise

avg_usage()