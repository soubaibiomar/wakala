import logging
import json
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, text

from .alerts import send_alert

logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self, site: str, threshold: float = 0.5):
        self.site = site
        self.threshold = threshold
        self.total_attempted = 0
        self.total_valid = 0
        self.field_successes = {}
        
    def record_attempt(self):
        self.total_attempted += 1
        
    def record_success(self, listing: dict):
        self.total_valid += 1
        # Track success per field
        for key, val in listing.items():
            if key not in self.field_successes:
                self.field_successes[key] = 0
            if val is not None and val != "unknown" and val != "":
                self.field_successes[key] += 1
                
    def finalize_run(self):
        """Calculate rates, save to DB, and alert if needed"""
        if self.total_attempted == 0:
            logger.info(f"No listings attempted for {self.site}")
            return
            
        success_rate = self.total_valid / self.total_attempted
        
        field_rates = {}
        for field, count in self.field_successes.items():
            field_rates[field] = count / self.total_attempted
            
        # Log results
        logger.info(f"Health Monitor for {self.site}: Success Rate = {success_rate:.1%}")
        for field, rate in field_rates.items():
            logger.info(f"  - {field}: {rate:.1%}")
            
        # Trigger alert if below threshold
        failing_fields = []
        for field, rate in field_rates.items():
            if rate < self.threshold:
                failing_fields.append(field)
                
        if success_rate < self.threshold or failing_fields:
            msg = f"Degradation detected for {self.site}. Success rate: {success_rate:.1%} (Threshold: {self.threshold:.1%})"
            send_alert(self.site, msg, severity="WARNING", details={"field_rates": field_rates})
            
            # Trigger selector regenerator if we have a generally ok response but specific fields failed
            if failing_fields and success_rate > 0.1: # Don't trigger if the site is totally blocked
                try:
                    import threading
                    from .selector_regenerator import SelectorRegenerator
                    
                    def run_regeneration():
                        regenerator = SelectorRegenerator()
                        regenerator.regenerate_selectors(self.site, failing_fields)
                        
                    thread = threading.Thread(target=run_regeneration)
                    thread.daemon = True
                    thread.start()
                    logger.info(f"Started background selector regeneration for {self.site}, fields: {failing_fields}")
                except ImportError as e:
                    logger.warning(f"SelectorRegenerator not available: {e}")
                except Exception as e:
                    logger.error(f"Failed to start selector regeneration: {e}")
            
        # Save to DB
        self._save_to_db(success_rate, field_rates)
        
    def _save_to_db(self, success_rate: float, field_rates: dict):
        try:
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                logger.warning("DATABASE_URL not set, skipping DB save")
                return
            engine = create_engine(db_url)
            with engine.begin() as conn:
                # Check if table exists
                check = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'scraper_health')")).scalar()
                if not check:
                    logger.warning("Table scraper_health does not exist, skipping DB save")
                    return
                    
                sql = text("""
                    INSERT INTO scraper_health 
                    (site, run_timestamp, success_rate, field_success_rates, total_attempted, total_valid)
                    VALUES (:site, :run_timestamp, :success_rate, :field_success_rates, :total_attempted, :total_valid)
                """)
                conn.execute(sql, {
                    "site": self.site,
                    "run_timestamp": datetime.now(timezone.utc),
                    "success_rate": success_rate,
                    "field_success_rates": json.dumps(field_rates),
                    "total_attempted": self.total_attempted,
                    "total_valid": self.total_valid
                })
        except Exception as e:
            logger.error(f"Failed to save health metrics to DB: {e}")
