-- Migration 009_require_phone.sql
-- Rend le champ téléphone obligatoire (NOT NULL)

-- 1. Attribuer un numéro par défaut temporaire aux anciens utilisateurs qui n'en ont pas
UPDATE users SET phone = '+212600000000' WHERE phone IS NULL;

-- 2. Rendre la colonne NOT NULL
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;
