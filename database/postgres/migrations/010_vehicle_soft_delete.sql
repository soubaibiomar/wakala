CREATE TYPE vehicle_status AS ENUM ('available', 'sold', 'deleted');

ALTER TABLE vehicles 
ADD COLUMN IF NOT EXISTS status vehicle_status NOT NULL DEFAULT 'available';

ALTER TABLE vehicles 
ADD COLUMN IF NOT EXISTS source_url VARCHAR(500);
