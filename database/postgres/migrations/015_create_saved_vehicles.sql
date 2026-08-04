-- ═══════════════════════════════════════════════════════════════
-- Wakala — Migration 015 : Create saved_vehicles table
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS saved_vehicles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, vehicle_id)
);

CREATE INDEX IF NOT EXISTS idx_saved_vehicles_user_id ON saved_vehicles(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_vehicles_vehicle_id ON saved_vehicles(vehicle_id);
