-- Vehicles
CREATE TABLE vehicles (
    vin VARCHAR(17) PRIMARY KEY,
    manufacturer_name VARCHAR(255) NOT NULL,
    description TEXT,
    horse_power INTEGER NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    model_year INTEGER NOT NULL,
    purchase_price NUMERIC(12, 2) NOT NULL,
    fuel_type VARCHAR(50) NOT NULL
);

-- For hashing VINs
CREATE SEQUENCE vehicle_id_seq START 1;