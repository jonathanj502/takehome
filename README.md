# Vehicle Management API

A FastAPI-based REST API for managing vehicle records with PostgreSQL database.

## Features

- Complete CRUD operations for vehicle management
- PostgreSQL database with schema validation
- System-generated unique VINs using SHA256 hashing
- Case-insensitive VIN lookups (LOWER function)
- Custom exception handling for JSON parsing vs validation errors
- RESTful API design with proper HTTP status codes

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **psycopg2** - PostgreSQL adapter
- **Pydantic** - Data validation

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 14+

### Installation

1. Clone the repository:
```bash
git clone https://github.com/jonathanj502/takehome.git
cd Takehome
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install fastapi uvicorn psycopg2-binary pytest
```

4. Set up the database:
```bash
psql postgres
CREATE DATABASE apollo_take_home;
\c apollo_take_home
\i schema.sql
```

## Running the Application

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

## API Endpoints

### GET /
Health check endpoint

**Response**: 200 OK
```json
{
  "message": "Vehicle Management API is running",
  "status": "healthy",
  "database": "connected"
}
```

### POST /vehicle
Create a new vehicle with system-generated VIN

The VIN is automatically generated from a sequence ID using SHA256 hashing. Do not include a VIN in the request body.

**Request Body**:
```json
{
  "manufacturer_name": "Honda",
  "description": "Blue sedan",
  "horse_power": 192,
  "model_name": "Accord",
  "model_year": 2021,
  "purchase_price": 25000.00,
  "fuel_type": "Gasoline"
}
```

**Response**: 201 Created
```json
{
  "vin": "8K9P5M2L7Q3R1X4Y6Z",
  "manufacturer_name": "Honda",
  "description": "Blue sedan",
  "horse_power": 192,
  "model_name": "Accord",
  "model_year": 2021,
  "purchase_price": 25000.00,
  "fuel_type": "Gasoline"
}
```

### GET /vehicle
Get all vehicles

**Response**: 200 OK
```json
[
  {
    "vin": "8K9P5M2L7Q3R1X4Y6Z",
    "manufacturer_name": "Honda",
    "description": "Blue sedan",
    "horse_power": 192,
    "model_name": "Accord",
    "model_year": 2021,
    "purchase_price": 25000.00,
    "fuel_type": "Gasoline"
  }
]
```

### GET /vehicle/{vin}
Retrieve a vehicle by VIN (case-insensitive)

**Response**: 200 OK
```json
{
  "vin": "8K9P5M2L7Q3R1X4Y6Z",
  "manufacturer_name": "Honda",
  "description": "Blue sedan",
  "horse_power": 192,
  "model_name": "Accord",
  "model_year": 2021,
  "purchase_price": 25000.00,
  "fuel_type": "Gasoline"
}
```

**Error Responses**:
- 404 Not Found: Vehicle with given VIN does not exist

### PUT /vehicle/{vin}
Update an existing vehicle by VIN (case-insensitive)

**Request Body**:
```json
{
  "manufacturer_name": "Honda",
  "description": "Red sedan with sunroof",
  "horse_power": 210,
  "model_name": "Accord",
  "model_year": 2022,
  "purchase_price": 27000.00,
  "fuel_type": "Hybrid"
}
```

**Response**: 200 OK with updated vehicle

**Error Responses**:
- 404 Not Found: Vehicle with given VIN does not exist
- 422 Unprocessable Entity: Invalid or missing fields in request body

### DELETE /vehicle/{vin}
Delete a vehicle by VIN (case-insensitive)

**Response**: 204 No Content

**Error Responses**:
- 404 Not Found: Vehicle with given VIN does not exist

## Error Handling

The API implements custom error handling to distinguish between different types of errors:

- **400 Bad Request**: Invalid JSON format in request body
- **404 Not Found**: Requested vehicle does not exist
- **422 Unprocessable Entity**: Validation error (invalid field types or missing required fields)
- **500 Internal Server Error**: Database operation failure
- **503 Service Unavailable**: Database connection failure

## Testing

Run the test suite to validate all endpoints and business logic:

```bash
pytest test_main.py -v
```

The test suite includes:
- Unit tests for VIN generation
- Pydantic model validation tests
- Integration tests for all CRUD endpoints
- Error handling and edge case tests
- Case-insensitivity verification

## Database Schema

See `schema.sql` for the complete database schema.