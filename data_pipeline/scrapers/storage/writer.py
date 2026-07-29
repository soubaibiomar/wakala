import json
import os
import uuid
import logging
from typing import List, Dict, Any

try:
    import psycopg2
    from psycopg2.extras import execute_values
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

from models.listing import Listing, ModelCatalogEntry

logger = logging.getLogger(__name__)

class DataWriter:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def write_jsonl(self, filename: str, data: List[Any]):
        """
        Write a list of Pydantic models to a JSON Lines file.
        """
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'a', encoding='utf-8') as f:
            for item in data:
                f.write(item.model_dump_json() + '\n')
        logger.info(f"Wrote {len(data)} items to {filepath}")

    def upsert_to_postgres(self, db_url: str, listings: List[Listing], default_seller_id: str):
        """
        Upsert listings directly into the PostgreSQL 'vehicles' table.
        """
        if not HAS_POSTGRES:
            logger.error("psycopg2 is not installed. Cannot write to Postgres.")
            return

        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # Build tuples for insertion
        vehicle_tuples = []
        listing_tuples = []
        
        for l in listings:
            # We map the unified Listing model to the vehicles table schema
            v_id = str(uuid.uuid4())
            l_id = str(uuid.uuid4())
            
            # Mileage is 0 if new, otherwise preserve the parsed mileage (which might be None)
            final_mileage = 0 if l.condition == "new" else l.mileage_km
            
            vehicle_tuples.append((
                v_id,
                default_seller_id,
                l.brand,
                l.model,
                l.year,
                l.price_mad,
                final_mileage,
                l.fuel_type,
                "berline",  # fallback body_type for now if not provided
                l.transmission,
                5, # doors
                5, # seats
                l.city,
                l.description or "",
                l.url,
                85.0 # mock condition_score for scraped cars
            ))
            
            listing_tuples.append((
                l_id,
                v_id,
                "active",
                [img for img in l.images]
            ))

        query_vehicles = """
            INSERT INTO vehicles (
                id, seller_id, brand, model, year, price, mileage,
                fuel_type, body_type, transmission, doors, seats, city,
                description, source_url, condition_score, created_at, updated_at
            ) VALUES %s
            ON CONFLICT (source_url) DO UPDATE SET
                price = EXCLUDED.price,
                mileage = EXCLUDED.mileage,
                updated_at = NOW()
            RETURNING id
        """
        
        query_listings = """
            INSERT INTO listings (
                id, vehicle_id, status, images_urls, created_at, updated_at
            ) VALUES %s
        """
        
        try:
            # Execute vehicles insertion
            # We need to construct the tuples for %s which includes created_at and updated_at handled in query or we can just append NOW() in query
            query_v = """
                INSERT INTO vehicles (
                    id, seller_id, brand, model, year, price, mileage,
                    fuel_type, body_type, transmission, doors, seats, city,
                    description, source_url, condition_score, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
                ON CONFLICT (source_url) DO UPDATE SET
                    price = EXCLUDED.price,
                    mileage = EXCLUDED.mileage,
                    updated_at = NOW()
                RETURNING id
            """
            
            query_l = """
                INSERT INTO listings (
                    id, vehicle_id, status, images_urls, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, NOW(), NOW()
                )
            """
            
            # Since execute_values is for a single query with %s, let's format it.
            v_template = "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"
            
            v_ids_returned = execute_values(cursor, """
                INSERT INTO vehicles (
                    id, seller_id, brand, model, year, price, mileage,
                    fuel_type, body_type, transmission, doors, seats, city,
                    description, source_url, condition_score, created_at, updated_at
                ) VALUES %s
                ON CONFLICT (source_url) DO UPDATE SET
                    price = EXCLUDED.price,
                    mileage = EXCLUDED.mileage,
                    description = EXCLUDED.description,
                    updated_at = NOW()
                RETURNING id, source_url
            """, vehicle_tuples, template=v_template, fetch=True)
            
            # Re-map vehicle_ids in case of conflict update where id might be the old one
            # v_ids_returned gives us (id, source_url). We need to map source_url -> actual vehicle_id
            url_to_vid = {row[1]: row[0] for row in v_ids_returned}
            
            final_listing_tuples = []
            for i, l in enumerate(listings):
                actual_vid = url_to_vid.get(l.url)
                if actual_vid:
                    final_listing_tuples.append((
                        str(uuid.uuid4()),
                        actual_vid,
                        "active",
                        [img for img in l.images]
                    ))
            
            # Clear existing listings for these vehicles (to avoid duplicates on upsert)
            if url_to_vid.values():
                cursor.execute("DELETE FROM listings WHERE vehicle_id = ANY(%s)", (list(url_to_vid.values()),))
            
            l_template = "(%s, %s, %s, %s::text[], NOW(), NOW())"
            execute_values(cursor, """
                INSERT INTO listings (
                    id, vehicle_id, status, images_urls, created_at, updated_at
                ) VALUES %s
            """, final_listing_tuples, template=l_template)
            
            conn.commit()
            logger.info(f"Successfully upserted {len(vehicle_tuples)} vehicles and listings to PostgreSQL.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to upsert to PostgreSQL: {e}")
            import traceback
            traceback.print_exc()
        finally:
            cursor.close()
            conn.close()
