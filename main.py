from fastapi import FastAPI, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from contextlib import contextmanager
import psycopg2
import hashlib

# Inits: DB connections and FastAPI app
DATABASE_URL = "postgresql://jonathanj@localhost/apollo_take_home"
app = FastAPI(
    title="Vehicle Management API",
    description="CRUD API for managing vehicle records",
    version="1.0.0"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler to distinguish between JSON parsing errors (400) 
    and validation errors (422).
    """
    errors = exc.errors()
    
    # JSON parsing errors have type 'json_invalid' or similar
    for error in errors:
        if error.get('type') in ['json_invalid', 'json_type']:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": "Invalid JSON format - cannot parse request body",
                    "errors": errors
                }
            )
    
    # Otherwise, it's a validation error (422)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error - invalid or missing fields",
            "errors": errors
        }
    )

def generate_vin(vehicle_id: int) -> str:
    """Generate a unique 17-character VIN."""
    chars = '0123456789ABCDEFGHJKLMNPRSTUVWXYZ'  # No I, O, Q
    hash_bytes = hashlib.sha256(str(vehicle_id).encode()).digest()
    vin = ''.join(chars[hash_bytes[i] % len(chars)] for i in range(17))
    return vin

# Pydantic models for request/response
class VehicleCreate(BaseModel):
    manufacturer_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    horse_power: int
    model_name: str = Field(..., min_length=1, max_length=255)
    model_year: int
    purchase_price: float
    fuel_type: str = Field(..., max_length=50)

class VehicleResponse(BaseModel):
    vin: str
    manufacturer_name: str
    description: Optional[str]
    horse_power: int
    model_name: str
    model_year: int
    purchase_price: float
    fuel_type: str


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Automatically handles:
    - Creating a new connection
    - Committing transactions on success
    - Rolling back transactions on error
    - Closing the connection when done
    """

    conn = None
    try:
        # Create a new database connection
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
        # Commit the transaction if no errors occurred
        conn.commit()
    except Exception as e:
        # Roll back the transaction if an error occurred
        if conn:
            conn.rollback()
        raise e
    finally:
        # Always close the connection to free resources
        if conn:
            conn.close()

@app.get("/")
async def root():
    """
    Health check endpoint to verify API and database connectivity.
    Returns basic API information and database connection status.
    """
    try:
        # Test database connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
            cursor.close()
        
        return {
            "message": "Vehicle Management API is running",
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        # Return error status if database connection fails
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        ) from e

@app.get("/vehicle", response_model=List[VehicleResponse])
def get_vehicle():
    """
    Return all vehicles in JSON format.
    Response on success: 200 OK with list of vehicles.
    Response on failure: 500 Internal Server Error if database operation fails.
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vehicles;")
            vehicles = cursor.fetchall()
            cursor.close()
            
            # Convert to list of dicts matching VehicleResponse schema
            vehicles_list: List[dict] = []
            for v in vehicles:
                vehicles_list.append({
                    "vin": v[0],
                    "manufacturer_name": v[1],
                    "description": v[2],
                    "horse_power": v[3],
                    "model_name": v[4],
                    "model_year": v[5],
                    "purchase_price": float(v[6]),
                    "fuel_type": v[7]
                })
            return vehicles_list
    except Exception as e:
        # Return 500 error if database operation fails
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve vehicles from database"
        ) from e

@app.post("/vehicle", status_code=status.HTTP_201_CREATED, response_model=VehicleResponse)
def create_vehicle(vehicle: VehicleCreate):
    """
    Create a new vehicle with system-generated unique VIN.
    The system automatically generates a valid 17-character VIN from a sequence.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get next sequence value
            cursor.execute("SELECT nextval('vehicle_id_seq')")
            vehicle_id = cursor.fetchone()[0]
            
            # Generate VIN from ID using hash function
            vin = generate_vin(vehicle_id)
            
            insert_query = """
                INSERT INTO vehicles (vin, manufacturer_name, description, horse_power, model_name, model_year, purchase_price, fuel_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING vin, manufacturer_name, description, horse_power, model_name, model_year, purchase_price, fuel_type;
            """
            cursor.execute(insert_query, (
                vin,
                vehicle.manufacturer_name,
                vehicle.description,
                vehicle.horse_power,
                vehicle.model_name,
                vehicle.model_year,
                vehicle.purchase_price,
                vehicle.fuel_type
            ))
            new_vehicle = cursor.fetchone()
            cursor.close()
            
            return VehicleResponse(
                vin=new_vehicle[0],
                manufacturer_name=new_vehicle[1],
                description=new_vehicle[2],
                horse_power=new_vehicle[3],
                model_name=new_vehicle[4],
                model_year=new_vehicle[5],
                purchase_price=float(new_vehicle[6]),
                fuel_type=new_vehicle[7]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create new vehicle"
        ) from e

@app.get("/vehicle/{vin}", response_model=VehicleResponse)
def get_vehicle_by_vin(vin: str):
    """
    Retrieve a vehicle by its VIN.
    Response on success: 200 OK with vehicle details.
    Response on failure: 404 Not Found if vehicle does not exist, 500 Internal Server
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vehicles WHERE LOWER(vin) = LOWER(%s);", (vin,))
            vehicle = cursor.fetchone()
            cursor.close()
            if vehicle is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
            return VehicleResponse(
                vin=vehicle[0],
                manufacturer_name=vehicle[1],
                description=vehicle[2],
                horse_power=vehicle[3],
                model_name=vehicle[4],
                model_year=vehicle[5],
                purchase_price=float(vehicle[6]),
                fuel_type=vehicle[7]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve vehicle"
        ) from e

@app.put("/vehicle/{vin}", response_model=VehicleResponse)
def update_vehicle(vin: str, vehicle: VehicleCreate):
    """
    Update an existing vehicle identified by its VIN.
    Response on success: 200 OK with updated vehicle details.
    Response on failure: 404 Not Found if vehicle does not exist, 500 Internal Server Error if update fails.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            update_query = """
                UPDATE vehicles
                SET manufacturer_name = %s,
                    description = %s,
                    horse_power = %s,
                    model_name = %s,
                    model_year = %s,
                    purchase_price = %s,
                    fuel_type = %s
                WHERE LOWER(vin) = LOWER(%s)
                RETURNING vin, manufacturer_name, description, horse_power, model_name, model_year, purchase_price, fuel_type;
            """
            cursor.execute(update_query, (
                vehicle.manufacturer_name,
                vehicle.description,
                vehicle.horse_power,
                vehicle.model_name,
                vehicle.model_year,
                vehicle.purchase_price,
                vehicle.fuel_type,
                vin
            ))
            updated_vehicle = cursor.fetchone()
            cursor.close()
            if updated_vehicle is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
            return VehicleResponse(
                vin=updated_vehicle[0],
                manufacturer_name=updated_vehicle[1],
                description=updated_vehicle[2],
                horse_power=updated_vehicle[3],
                model_name=updated_vehicle[4],
                model_year=updated_vehicle[5],
                purchase_price=float(updated_vehicle[6]),
                fuel_type=updated_vehicle[7]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update vehicle"
        ) from e
    
@app.delete("/vehicle/{vin}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vin: str):
    """
    Delete a vehicle by its VIN.
    Response on success: 204 No Content.
    Response on failure: 404 Not Found if vehicle does not exist, 500 Internal Server Error if deletion fails.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vehicles WHERE LOWER(vin) = LOWER(%s) RETURNING vin;", (vin,))
            deleted_vehicle = cursor.fetchone()
            cursor.close()
            if deleted_vehicle is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
            return
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete vehicle"
        ) from e
    
if __name__ == "__main__":
    import uvicorn
    # Run the application with hot reload enabled for development
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )