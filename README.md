# Teknasyon BI Data Engineering Case

## Database Schema

### 1. `customers`
Contains customer-related information:
- **Columns:**
  - `customer_id`: Unique identifier for each customer.
  - `name`: Customer's name.
  - `email`: Customer's email address.
  - `phone`: Customer's phone number.
  - `created_at`: Timestamp of when the customer was added.

### 2. `subscriptions`
Tracks subscriptions associated with customers:
- **Columns:**
  - `subscription_id`: Unique identifier for each subscription.
  - `customer_id`: Foreign key linking to the `customers` table.
  - `subscription_type`: Type of subscription (e.g., Basic, Premium, Enterprise).
  - `start_date`: Start date of the subscription.
  - `end_date`: End date of the subscription.

### 3. `payments`
Logs payments for subscriptions:
- **Columns:**
  - `payment_id`: Unique identifier for each payment.
  - `subscription_id`: Foreign key linking to the `subscriptions` table.
  - `payment_date`: Timestamp of the payment.
  - `amount`: Amount paid for the subscription.

### 4. `usage`
Records service usage metrics:
- **Columns:**
  - `usage_id`: Unique identifier for each usage record.
  - `subscription_id`: Foreign key linking to the `subscriptions` table.
  - `data_usage`: Data consumed (in GB).
  - `call_minutes`: Minutes spent on calls.
  - `sms_count`: Number of SMS sent.

## Flask API Endpoints

The Flask application provides RESTful API endpoints to retrieve data from the database tables.

### Common Parameters
- `page` (optional): Page number for pagination (default: 1).
- `per_page` (optional): Number of records per page (default: 10).

### Endpoints

1. **Get Customers**  
   **Endpoint:** `/customers`  
   **Method:** `GET`  
   **Example Request:** 
GET /customers?page=1&per_page=2
**Example Response:**
```json
[
    {
        "customer_id": 1,
        "name": "JohnDoe",
        "email": "johndoe@example.com",
        "phone": "+1234567890",
        "created_at": "2024-12-02T12:00:00"
    },
    {
        "customer_id": 2,
        "name": "JaneSmith",
        "email": "janesmith@example.com",
        "phone": "+1234567891",
        "created_at": "2024-12-02T12:05:00"
    }
]
```
2. **Get Subscriptions**  
   **Endpoint:** `/subscriptions`  
   **Method:** `GET`  
   **Example Request:** 
GET /subscriptions?page=1&per_page=2
```json
[
    {
        "subscription_id": 1,
        "customer_id": 1,
        "subscription_type": "Premium",
        "start_date": "2024-01-01",
        "end_date": "2025-01-01"
    },
    {
        "subscription_id": 2,
        "customer_id": 2,
        "subscription_type": "Basic",
        "start_date": "2024-02-01",
        "end_date": "2025-02-01"
    }
]
```
3. **Get Payments**  
   **Endpoint:** `/payments`  
   **Method:** `GET`  
   **Example Request:** 
GET /payments?page=1&per_page=2
```json
[
    {
        "payment_id": 1,
        "subscription_id": 1,
        "payment_date": "2024-12-01T12:34:56",
        "amount": 50.00
    },
    {
        "payment_id": 2,
        "subscription_id": 2,
        "payment_date": "2024-12-02T15:20:00",
        "amount": 70.00
    }
]
```
4. **Get Usuage**  
   **Endpoint:** `/usage`  
   **Method:** `GET`  
   **Example Request:** 
GET /usage?page=1&per_page=2
```json
[
    {
        "usage_id": 1,
        "subscription_id": 1,
        "data_usage": 5.5,
        "call_minutes": 45.3,
        "sms_count": 10
    },
    {
        "usage_id": 2,
        "subscription_id": 2,
        "data_usage": 3.2,
        "call_minutes": 25.0,
        "sms_count": 20
    }
]

```
5**Post Payment Amount**  
   **Endpoint:** `/payment_amount`  
   **Method:** `POST, GET`  
   **Example Request POST:**
POST /payment_amount
```json
[
    {"customer_id": 1, "sum_payment": 100.50},
    {"customer_id": 2, "sum_payment": 200.00}
]
```
**Example Request GET:**
GET /payment_amount?page=1&per_page=2
```json
[
    {
        "id": 1,
        "customer_id": 1,
        "sum_payment": 100.50
    },
    {
        "id": 2,
        "customer_id": 2,
        "sum_payment": 200.00
    }
]
```

---

Feel free to use this case to test your SQL and data analysis skills!
