-- ═══════════════════════════════════════════════════════════════
-- Wakala — Migration 014 : Extension du champ Source
-- Ajout des nouvelles plateformes et support des concessionnaires
-- ═══════════════════════════════════════════════════════════════

-- Note : Dans l'état actuel de la base, le champ 'source' n'est 
-- pas contraint au niveau PostgreSQL par un ENUM ou un CHECK restrictif 
-- sur la table listings ou vehicles, mais il est vérifié 
-- par le SchemaValidator en Python.
--
-- Cette migration prépare une structure formelle si la colonne 
-- 'source' est explicitement ajoutée avec contrainte dans 
-- une table 'raw_listings' ou similaire.

DO $$ BEGIN
    -- Si la colonne source existe dans listings, on peut lui 
    -- appliquer un CHECK pour plus de rigueur.
    -- (Optionnel, commenté si la table n'a pas encore cette colonne)
    
    /*
    ALTER TABLE listings 
    ADD CONSTRAINT ck_listings_source 
    CHECK (
        source IN ('avito', 'moteur', 'wandaloo', 'leguideauto', 
                  'globaloccaz', 'otoclic', 'kifal', 'carz', 'spoticar')
        OR source LIKE 'dealer_%'
    );
    */
    
    -- Pour la table scraper_health (déjà existante)
    -- On s'assure que la colonne site est assez large pour "dealer_nom_tres_long"
    ALTER TABLE scraper_health ALTER COLUMN site TYPE VARCHAR(100);

EXCEPTION WHEN others THEN
    -- Ignore error if tables don't exist yet
    NULL;
END $$;
