import psycopg2
import random
import string
import logging
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Starting data generation script...")

db_params = {
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'dbname': os.getenv('POSTGRES_DB', 'telco_db'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise


def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        logging.info("Dropping existing tables if any...")
        cur.execute("DROP TABLE IF EXISTS usage, payments, subscriptions, customers, payment_amount CASCADE;")
        logging.info("Creating 'customers' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255),
                phone VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        logging.info("Creating 'subscriptions' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id SERIAL PRIMARY KEY,
                customer_id INTEGER REFERENCES customers(customer_id),
                subscription_type VARCHAR(50),
                start_date DATE,
                end_date DATE
            );
        """)
        logging.info("Creating 'payments' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id SERIAL PRIMARY KEY,
                subscription_id INTEGER REFERENCES subscriptions(subscription_id),
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                amount DECIMAL(10, 2)
            );
        """)
        logging.info("Creating 'usage' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usage (
                usage_id SERIAL PRIMARY KEY,
                subscription_id INTEGER REFERENCES subscriptions(subscription_id),
                data_usage DECIMAL(10, 2),
                call_minutes DECIMAL(10, 2),
                sms_count INTEGER
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS payment_amount (
                id SERIAL PRIMARY KEY,
                customer_id INT NOT NULL,
                sum_payment NUMERIC(10, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        logging.info("Tables created successfully.")
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
    finally:
        cur.close()
        conn.close()


def insert_data_to_db():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        logging.info("Inserting customer data...")
        for _ in range(500):
            name = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=10))
            email = f"{name.lower()}@example.com"
            phone = f"+1{random.randint(1000000000, 9999999999)}"
            cur.execute("""
            INSERT INTO customers (name, email, phone) 
            VALUES (%s, %s, %s)
            """, (name, email, phone))
        logging.info("Inserted 500 customer records.")
        logging.info("Inserting subscription data...")
        for _ in range(500):
            customer_id = random.randint(1, 500)
            subscription_type = random.choice(["Basic", "Premium", "Enterprise"])
            start_date = f"2024-01-01"
            end_date = f"2025-01-01"
            cur.execute("""
            INSERT INTO subscriptions (customer_id, subscription_type, start_date, end_date)
            VALUES (%s, %s, %s, %s)
            """, (customer_id, subscription_type, start_date, end_date))
        logging.info("Inserted 500 subscription records.")
        logging.info("Inserting payment data...")
        for _ in range(500):
            subscription_id = random.randint(1, 500)
            amount = round(random.uniform(10.0, 100.0), 2)
            cur.execute("""
            INSERT INTO payments (subscription_id, amount)
            VALUES (%s, %s)
            """, (subscription_id, amount))
        logging.info("Inserted 500 payment records.")
        logging.info("Inserting usage data...")
        for _ in range(500):
            subscription_id = random.randint(1, 500)
            data_usage = round(random.uniform(0.1, 10.0), 2)
            call_minutes = round(random.uniform(1.0, 100.0), 2)
            sms_count = random.randint(0, 100)
            cur.execute("""
            INSERT INTO usage (subscription_id, data_usage, call_minutes, sms_count)
            VALUES (%s, %s, %s, %s)
            """, (subscription_id, data_usage, call_minutes, sms_count))
        logging.info("Inserted 500 usage records.")

        conn.commit()
        logging.info("Data insertion completed successfully.")
    except Exception as e:
        logging.error(f"Error inserting data: {e}")
    finally:
        cur.close()
        conn.close()
