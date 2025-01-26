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

####
base_url = "http://localhost:5001"
customers_endpoint = f"{base_url}/customers"
subscriptions_endpoint = f"{base_url}/subscriptions"
payments_endpoint = f"{base_url}/payments"
####


def extract_data(api_endpoint, days=30):
    """Extract data from the API for the last days days."""
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

customers = extract_data(customers_endpoint)  # Fetch customers data
subscriptions = extract_data(subscriptions_endpoint)  # Fetch subscriptions data
payments = extract_data(payments_endpoint)  # Fetch payments data

######

def transform_data(customers, subscriptions, payments):
    """Aggregate payment data by customer while handling missing subscription IDs."""
    # Step 1: Create subscription_id -> customer_id mapping
    subscription_to_customer = {
        subscription["subscription_id"]: subscription["customer_id"]
        for subscription in subscriptions
    }
    
    logging.info("Subsricipton to customer:")
    for subscription_id,customer_id in subscription_to_customer.items():
        logging.info(f"Subs ID:{subscription_id}, CUstomer ID : {customer_id}")

    # Log missing subscription IDs during aggregation
    missing_subscription_ids = set()
    customer_payments = {}

    for payment in payments:
        subscription_id_payment = payment.get("subscription_id")
        amount = float(payment.get("amount", 0))

        if subscription_id in subscription_to_customer == subscription_id_payment:
            # Map subscription_id to customer_id and aggregate payments
            customer_id = subscription_to_customer[subscription_id]
            customer_payments[customer_id] = customer_payments.get(customer_id, 0) + amount
        else:
            # Log missing subscription_id
            missing_subscription_ids.add(subscription_id)

    
    # Log all missing subscription IDs
    """"
    if missing_subscription_ids:
        logging.warning(f"Missing subscription IDs: {missing_subscription_ids}")
    """
    # Step 2: Create final transformed data with all customers
    transformed_data = []
    for subscription in subscriptions:
        customer_id = customer["customer_id"]
        sum_payment = customer_payments.get(customer_id, 0)  # Default to 0 if no payments
        transformed_data.append({
            "customer_id": customer_id,
            "sum_payment": sum_payment
        })

    # Log the final aggregation
    
    logging.info("Final Transformed Data:")
    for record in transformed_data:
        logging.info(record)
    
    return transformed_data


transformed_data = transform_data(customers,subscriptions,payments)
##Load the data into db##

def load_data_to_db(transformed_data):
    """Load transformed data into the database."""
    try:
        logging.info("Connecting to the database...")
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
        logging.info("Data successfully loaded into the database.")
    except Exception as e:
        logging.error(f"Failed to load data into the database: {e}")
        raise

api_endpoint_app = "http://localhost:5001/payment_amount"
def load_data_to_api(transformed_data, api_endpoint_app):
    """Load transformed data to the /payment_amount API endpoint."""
    try:
        logging.info(f"Loading data into API endpoint {api_endpoint_app}...")
        response = requests.post(api_endpoint_app, json=transformed_data)
        response.raise_for_status()
        logging.info("Data successfully loaded into the API.")
    except Exception as e:
        logging.error(f"Failed to load data into API endpoint {api_endpoint_app}: {e}")
        raise

  # Load to database
load_data_to_api(transformed_data,api_endpoint_app)