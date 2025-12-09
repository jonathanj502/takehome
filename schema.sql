-- Vehicles
CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    vin VARCHAR(17) UNIQUE NOT NULL,
    manufacturer_name VARCHAR(255) NOT NULL,
    description TEXT,
    horse_power INTEGER NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    model_year INTEGER NOT NULL,
    purchase_price NUMERIC(12, 2) NOT NULL,
    fuel_type VARCHAR(50) NOT NULL,
    vin_lower VARCHAR(17) GENERATED ALWAYS AS (LOWER(vin)) STORED,
    UNIQUE(vin_lower)
);