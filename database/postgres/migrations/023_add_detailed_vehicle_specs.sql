-- Detailed Morocco catalogue technical-sheet fields.
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS width_cm INTEGER;
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS height_cm INTEGER;
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS official_consumption NUMERIC(5,2);
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS real_consumption NUMERIC(5,2);
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS electric_range_km INTEGER;
