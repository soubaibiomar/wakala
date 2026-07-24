-- database/postgres/migrations/013_maintenance_module.sql

CREATE TABLE IF NOT EXISTS vehicle_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    car_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    service_type VARCHAR(100) NOT NULL,
    mileage INTEGER NOT NULL,
    date DATE NOT NULL,
    cost NUMERIC(10, 2),
    receipt_url VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vehicle_services_car_id ON vehicle_services(car_id);
CREATE INDEX IF NOT EXISTS idx_vehicle_services_user_id ON vehicle_services(user_id);
CREATE INDEX IF NOT EXISTS idx_vehicle_services_date ON vehicle_services(date);

CREATE TABLE IF NOT EXISTS service_reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    car_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    trigger_mileage INTEGER,
    trigger_date DATE,
    message VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_service_reminders_car_id ON service_reminders(car_id);
