Instructions to Run the Project
1. Clone the Repository
Clone this repository to your local machine:
####
2. Build and Start the Docker Containers
Build and start the required Docker containers using the following command:

bash
'''
docker-compose up --build
'''
This will set up all necessary services, including PostgreSQL, Flask, and Airflow.

3. Run the ETL Test Script
Execute the Etl_pipeline_test.py script to test the ETL pipeline:

bash
CopyEdit
MSYS_NO_PATHCONV=1 docker exec -it teknasyon-case-de-main-flask-app-1 python /app/sql_queries.py
This script:

Extracts, transforms, and loads data into the database.
Logs the process for debugging and verification.
4. Verify Results
From the Database:

Use pgAdmin or any SQL client to connect to the database.
Verify the data in the respective tables (e.g., customers, subscriptions).
From the API:

Access the API endpoints to confirm data insertion. For example:

http://localhost:5001/payment_amount

5. Access Airflow UI
Open the Airflow UI:

http://localhost:8080
Log in using the credentials:
Username: admin
Password: admin
Locate the DAGs and manually trigger the ETL pipeline tasks.
6. Run SQL Queries
Run the sql_queries.py script to analyze the data:

bash

MSYS_NO_PATHCONV=1 docker exec -it teknasyon-case-de-main-flask-app-1 python /app/sql_queries.py
This script allows you to:

Execute predefined SQL queries.
Analyze data trends or insights directly from the database.
7. Notes
Ensure you have Python and Docker installed on your system.
All configurations, such as database credentials and API endpoints, are defined in the .env file.
