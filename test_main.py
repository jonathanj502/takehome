import pytest
from fastapi.testclient import TestClient
from main import app, generate_vin

client = TestClient(app)


# Unit Tests - VIN Generation
class TestVINGeneration:
    def test_generate_vin_length(self):
        """Test that generated VIN is exactly 17 characters."""
        vin = generate_vin(1)
        assert len(vin) == 17

    def test_generate_vin_valid_characters(self):
        """Test that VIN only contains valid characters (no I, O, Q)."""
        invalid_chars = set('IOQ')
        for i in range(1, 100):
            vin = generate_vin(i)
            assert not any(char in invalid_chars for char in vin)

    def test_generate_vin_deterministic(self):INSERT INTO vehicles (
        vin,
        manufacturer_name,
        description,
        horse_power,
        model_name,
        model_year,
        purchase_price,
        fuel_type
      )
    VALUES (
        'vin:character varying',
        'manufacturer_name:character varying',
        'description:text',
        horse_power:integer,
        'model_name:character varying',
        model_year:integer,
        purchase_price:numeric,
        'fuel_type:character varying'
      );
        """Test that same ID always produces same VIN."""
        vin1 = generate_vin(42)
        vin2 = generate_vin(42)
        assert vin1 == vin2

    def test_generate_vin_unique(self):
        """Test that different IDs produce different VINs."""
        vin1 = generate_vin(1)
        vin2 = generate_vin(2)
        assert vin1 != vin2


# Unit Tests - Pydantic Models
class TestVehicleModels:
    def test_vehicle_create_valid(self):
        """Test valid VehicleCreate model."""
        from main import VehicleCreate
        vehicle = VehicleCreate(
            manufacturer_name="Honda",
            description="Blue sedan",
            horse_power=192,
            model_name="Accord",
            model_year=2021,
            purchase_price=25000.00,
            fuel_type="Gasoline"
        )
        assert vehicle.manufacturer_name == "Honda"
        assert vehicle.horse_power == 192

    def test_vehicle_create_missing_required_field(self):
        """Test VehicleCreate validation fails with missing required field."""
        from main import VehicleCreate
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            VehicleCreate(
                description="Blue sedan",
                horse_power=192,
                model_name="Accord",
                model_year=2021,
                purchase_price=25000.00,
                fuel_type="Gasoline"
                # Missing manufacturer_name
            )

    def test_vehicle_create_invalid_type(self):
        """Test VehicleCreate validation fails with wrong type."""
        from main import VehicleCreate
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            VehicleCreate(
                manufacturer_name="Honda",
                description="Blue sedan",
                horse_power="not_a_number",  # Should be int
                model_name="Accord",
                model_year=2021,
                purchase_price=25000.00,
                fuel_type="Gasoline"
            )

    def test_vehicle_create_optional_description(self):
        """Test that description is optional."""
        from main import VehicleCreate
        vehicle = VehicleCreate(
            manufacturer_name="Honda",
            horse_power=192,
            model_name="Accord",
            model_year=2021,
            purchase_price=25000.00,
            fuel_type="Gasoline"
        )
        assert vehicle.description is None


# Component Tests - Health Check
class TestHealthCheck:
    def test_root_endpoint(self):
        """Test root health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"


# Component Tests - POST /vehicle
class TestCreateVehicle:
    def test_create_vehicle_success(self):
        """Test successful vehicle creation returns 201."""
        response = client.post("/vehicle", json={
            "manufacturer_name": "Honda",
            "description": "Blue sedan",
            "horse_power": 192,
            "model_name": "Accord",
            "model_year": 2021,
            "purchase_price": 25000.00,
            "fuel_type": "Gasoline"
        })
        assert response.status_code == 201
        data = response.json()
        assert "vin" in data
        assert len(data["vin"]) == 17
        assert data["manufacturer_name"] == "Honda"

    def test_create_vehicle_invalid_data(self):
        """Test creation with invalid data returns 422."""
        response = client.post("/vehicle", json={
            "manufacturer_name": "Honda",
            "horse_power": "not_a_number",  # Invalid type
            "model_name": "Accord",
            "model_year": 2021,
            "purchase_price": 25000.00,
            "fuel_type": "Gasoline"
        })
        assert response.status_code == 422

    def test_create_vehicle_missing_required_field(self):
        """Test creation with missing required field returns 422."""
        response = client.post("/vehicle", json={
            "description": "Blue sedan",
            "horse_power": 192,
            "model_name": "Accord",
            "model_year": 2021,
            "purchase_price": 25000.00,
            "fuel_type": "Gasoline"
            # Missing manufacturer_name
        })
        assert response.status_code == 422

    def test_create_vehicle_malformed_json(self):
        """Test creation with malformed JSON returns 400."""
        response = client.post("/vehicle",
            content='{"manufacturer_name": "Honda"',  # Missing closing brace
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400


# Component Tests - GET /vehicle
class TestGetAllVehicles:
    def test_get_all_vehicles_success(self):
        """Test getting all vehicles returns 200."""
        response = client.get("/vehicle")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_all_vehicles_response_format(self):
        """Test all vehicles match VehicleResponse schema."""
        # First create a vehicle
        client.post("/vehicle", json={
            "manufacturer_name": "Honda",
            "horse_power": 192,
            "model_name": "Accord",
            "model_year": 2021,
            "purchase_price": 25000.00,
            "fuel_type": "Gasoline"
        })
        
        response = client.get("/vehicle")
        assert response.status_code == 200
        vehicles = response.json()
        
        if vehicles:  # If there are vehicles
            vehicle = vehicles[0]
            assert "vin" in vehicle
            assert "manufacturer_name" in vehicle
            assert "horse_power" in vehicle
            assert "model_name" in vehicle
            assert "model_year" in vehicle
            assert "purchase_price" in vehicle
            assert "fuel_type" in vehicle


# Component Tests - GET /vehicle/{vin}
class TestGetVehicleByVin:
    def test_get_vehicle_success(self):
        """Test retrieving vehicle by VIN returns 200."""
        # Create a vehicle
        create_response = client.post("/vehicle", json={
            "manufacturer_name": "Tesla",
            "horse_power": 450,
            "model_name": "Model S",
            "model_year": 2022,
            "purchase_price": 85000.00,
            "fuel_type": "Electric"
        })
        vin = create_response.json()["vin"]
        
        # Get the vehicle
        response = client.get(f"/vehicle/{vin}")
        assert response.status_code == 200
        data = response.json()
        assert data["vin"] == vin
        assert data["manufacturer_name"] == "Tesla"

    def test_get_vehicle_case_insensitive(self):
        """Test VIN lookup is case-insensitive."""
        # Create a vehicle
        create_response = client.post("/vehicle", json={
            "manufacturer_name": "Tesla",
            "horse_power": 450,
            "model_name": "Model S",
            "model_year": 2022,
            "purchase_price": 85000.00,
            "fuel_type": "Electric"
        })
        vin = create_response.json()["vin"]
        
        # Test with lowercase
        response = client.get(f"/vehicle/{vin.lower()}")
        assert response.status_code == 200
        assert response.json()["vin"] == vin

    def test_get_vehicle_not_found(self):
        """Test retrieving non-existent vehicle returns 404."""
        response = client.get("/vehicle/NONEXISTENT12345")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# Component Tests - PUT /vehicle/{vin}
class TestUpdateVehicle:
    def test_update_vehicle_success(self):
        """Test successful vehicle update returns 200."""
        # Create a vehicle
        create_response = client.post("/vehicle", json={
            "manufacturer_name": "Honda",
            "horse_power": 192,
            "model_name": "Accord",
            "model_year": 2021,
            "purchase_price": 25000.00,
            "fuel_type": "Gasoline"
        })
        vin = create_response.json()["vin"]
        
        # Update the vehicle
        response = client.put(f"/vehicle/{vin}", json={
            "manufacturer_name": "Toyota",
            "horse_power": 200,
            "model_name": "Camry",
            "model_year": 2022,
            "purchase_price": 30000.00,
            "fuel_type": "Hybrid"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["manufacturer_name"] == "Toyota"
        assert data["horse_power"] == 200

    def test_update_vehicle_case_insensitive(self):
        """Test update with case-insensitive VIN lookup."""
        # Create a vehicle
        create_response = client.post("/vehicle", json={
            "manufacturer_name": "Honda",
            "horse_power": 192,
            "model_name": "Accord",
            "model_year": 2021,
            "purchase_price": 25000.00,
            "fuel_type": "Gasoline"
        })
        vin = create_response.json()["vin"]
        
        # Update with lowercase VIN
        response = client.put(f"/vehicle/{vin.lower()}", json={
            "manufacturer_name": "Toyota",
            "horse_power": 200,
            "model_name": "Camry",
            "model_year": 2022,
            "purchase_price": 30000.00,
            "fuel_type": "Hybrid"
        })
        assert response.status_code == 200

    def test_update_vehicle_not_found(self):
        """Test updating non-existent vehicle returns 404."""
        response = client.put("/vehicle/NONEXISTENT12345", json={
            "manufacturer_name": "Toyota",
            "horse_power": 200,
            "model_name": "Camry",
            "model_year": 2022,
            "purchase_price": 30000.00,
            "fuel_type": "Hybrid"
        })
        assert response.status_code == 404

    def test_update_vehicle_invalid_data(self):
        """Test update with invalid data returns 422."""
        # Create a vehicle
        create_response = client.post("/vehicle", json={
            "manufacturer_name": "Honda",
            "horse_power": 192,
            "model_name": "Accord",
            "model_year": 2021,
            "purchase_price": 25000.00,
            "fuel_type": "Gasoline"
        })
        vin = create_response.json()["vin"]
        
        # Try to update with invalid data
        response = client.put(f"/vehicle/{vin}", json={
            "manufacturer_name": "Toyota",
            "horse_power": "not_a_number",  # Invalid type
            "model_name": "Camry",
            "model_year": 2022,
            "purchase_price": 30000.00,
            "fuel_type": "Hybrid"
        })
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
