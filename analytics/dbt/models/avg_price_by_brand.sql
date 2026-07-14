-- ═══════════════════════════════════════════════════════════════
-- dbt Model : Prix moyen par marque et modèle
-- Source : table vehicles (PostgreSQL)
-- ═══════════════════════════════════════════════════════════════

{{ config(materialized='table') }}

SELECT
    brand,
    model,
    fuel_type,
    COUNT(*) AS listing_count,
    ROUND(AVG(price)::numeric, 2) AS avg_price,
    ROUND(STDDEV(price)::numeric, 2) AS std_price,
    ROUND(AVG(mileage)::numeric, 0) AS avg_mileage,
    MIN(price) AS min_price,
    MAX(price) AS max_price
FROM {{ source('automind', 'vehicles') }}
WHERE is_active = TRUE
GROUP BY brand, model, fuel_type
ORDER BY listing_count DESC
