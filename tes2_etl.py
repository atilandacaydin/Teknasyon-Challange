import requests
import psycopg2
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

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


def change_db_schema():
    """Modify the database schema to add a unique constraint on customer_id."""
    alter_query = """
        ALTER TABLE payment_amount ADD CONSTRAINT unique_customer_id UNIQUE (customer_id);
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(alter_query)
        conn.commit()
        cur.close()
        conn.close()
        logging.info("Database schema successfully changed!")
    except Exception as e:
        logging.error(f"Failed to change database schema: {e}")


def extract_data(api_endpoint, days=30):
    """Extract data from the API for the last 'days' days."""
    try:
        # Calculate the date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Define query parameters
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }

        logging.info(f"Extracting data from {api_endpoint} for the last {days} days...")
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Failed to fetch data from {api_endpoint}: {e}")
        raise


def transform_data_using_sql():
    """Transform data using SQL and return the result."""
    query = """
        SELECT 
            s.customer_id,
            COALESCE(SUM(p.amount), 0) AS sum_payment
        FROM 
            subscriptions s
        LEFT JOIN 
            payments p ON s.subscription_id = p.subscription_id
        GROUP BY 
            s.customer_id;
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        conn.close()

        # Transform SQL results into a list of dictionaries
        transformed_data = [{"customer_id": row[0], "sum_payment": float(row[1])} for row in results]
        logging.info("Transformed Data:")
        for record in transformed_data:
            logging.info(record)

        return transformed_data
    except Exception as e:
        logging.error(f"Error during transformation: {e}")
        raise


def load_data_to_db(transformed_data):
    """Load the transformed data into the database."""
    if not transformed_data:
        logging.error("Transformed data is empty. Run transform_data_using_sql first.")
        return

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        insert_query = """
        INSERT INTO payment_amount (customer_id, sum_payment)
        VALUES (%s, %s)
        ON CONFLICT (customer_id) DO UPDATE
        SET sum_payment = EXCLUDED.sum_payment;
        """
        for record in transformed_data:
            cur.execute(insert_query, (record["customer_id"], record["sum_payment"]))
        conn.commit()
        cur.close()
        conn.close()
        logging.info("Data loaded successfully into the database.")
    except Exception as e:
        logging.error(f"Error loading data to the database: {e}")
        raise


def load_data_to_api(transformed_data, api_endpoint_app):
    """Load transformed data to the /payment_amount API endpoint."""
    if not transformed_data:
        logging.error("Transformed data is empty. Cannot load to API.")
        return

    # Wrap the data into a JSON object
    payload = {"data": transformed_data}

    try:
        logging.info(f"Loading data into API endpoint {api_endpoint_app}...")
        logging.info(f"Payload: {payload}")  # Log the formatted payload
        response = requests.post(api_endpoint_app, json=payload)
        logging.info(f"API Response: {response.status_code}, {response.text}")
        response.raise_for_status()
        logging.info("Data successfully loaded into the API.")
    except Exception as e:
        logging.error(f"Failed to load data into API endpoint {api_endpoint_app}: {e}")
        raise


if __name__== "__main__":
    # Step 1: Change database schema
    change_db_schema()

    # Step 2: Transform data using SQL
    transformed_data = transform_data_using_sql()

    # Step 3: Load data into the database
    load_data_to_db(transformed_data)

    # Step 4: Load data into the API
    api_endpoint_app = "http://localhost:5001/payment_amount"
    load_data_to_api(transformed_data, api_endpoint_app)