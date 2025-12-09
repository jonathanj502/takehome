# Vehicle Management API

A FastAPI-based REST API for managing vehicle records with PostgreSQL database.

## Features

- CRUD operations for vehicle management
- PostgreSQL database with schema validation
- Case-insensitive VIN uniqueness
- RESTful API design
- Interactive API documentation (Swagger UI)

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
git clone <your-repo-url>
cd Takehome
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install fastapi uvicorn psycopg2-binary
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

### GET /vehicle
Get all vehicles

**Response**: 200 OK
```json
[
  {
    "vin": "1HGBH41JXMN109186",
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

### POST /vehicle
Create a new vehicle

**Request Body**:
```json
{
  "vin": "1HGBH41JXMN109186",
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

## Database Schema

See `schema.sql` for the complete database schema.

## License

MIT
