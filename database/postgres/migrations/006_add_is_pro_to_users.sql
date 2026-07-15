-- Migration 006 : Ajout de la colonne is_pro pour le flag des courtiers cachés (GDS)

ALTER TABLE users ADD COLUMN IF NOT EXISTS is_pro BOOLEAN DEFAULT FALSE NOT NULL;
