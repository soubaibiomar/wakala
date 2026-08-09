import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

logger = logging.getLogger(__name__)

class SourceStateManager:
    def __init__(self):
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = os.getenv("POSTGRES_PORT", "5432")
        self.user = os.getenv("POSTGRES_USER", "wakala_user")
        self.password = os.getenv("POSTGRES_PASSWORD", "wakala_secret_password")
        self.dbname = os.getenv("POSTGRES_DB", "wakala")
        
        self.default_backoff = 3600  # 1 hour
        self.max_backoff = 86400  # 24 hours
        self.max_failures = 5

    def _get_connection(self):
        if not PSYCOPG2_AVAILABLE:
            raise RuntimeError("psycopg2 is not installed.")
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.dbname
        )

    def get_state(self, source_name: str) -> Dict[str, Any]:
        """Fetch the current state for a source, creating a default one if it doesn't exist."""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        "SELECT * FROM scraper_source_state WHERE source_name = %s",
                        (source_name,)
                    )
                    row = cur.fetchone()
                    
                    if row:
                        return dict(row)
                    
                    # Create default state
                    cur.execute(
                        """
                        INSERT INTO scraper_source_state 
                        (source_name, status, consecutive_failure_count, current_backoff_interval, selector_health_score)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING *
                        """,
                        (source_name, 'active', 0, self.default_backoff, 100.0)
                    )
                    conn.commit()
                    return dict(cur.fetchone())
        except Exception as e:
            logger.error(f"Failed to get/create state for {source_name}: {e}")
            # Return a fallback in-memory state if DB fails
            return {
                "source_name": source_name,
                "status": "active",
                "consecutive_failure_count": 0,
                "current_backoff_interval": self.default_backoff,
                "selector_health_score": 100.0,
                "last_run_at": None
            }

    def update_state(self, source_name: str, updates: Dict[str, Any]) -> None:
        """Update specific fields of the source state."""
        allowed_fields = {"status", "consecutive_failure_count", "current_backoff_interval", "selector_health_score", "last_run_at"}
        update_clauses = []
        values = []
        
        for k, v in updates.items():
            if k in allowed_fields:
                update_clauses.append(f"{k} = %s")
                values.append(v)
                
        if not update_clauses:
            return
            
        values.append(source_name)
        
        sql = f"UPDATE scraper_source_state SET {', '.join(update_clauses)} WHERE source_name = %s"
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, tuple(values))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update state for {source_name}: {e}")

    def record_success(self, source_name: str) -> None:
        """Reset failures and backoff."""
        self.update_state(source_name, {
            "status": "active",
            "consecutive_failure_count": 0,
            "current_backoff_interval": self.default_backoff,
            "last_run_at": datetime.now(timezone.utc)
        })

    def record_block_failure(self, source_name: str) -> None:
        """Handle Active Block: Double backoff, pause if threshold reached."""
        state = self.get_state(source_name)
        
        fails = state["consecutive_failure_count"] + 1
        new_backoff = min(state["current_backoff_interval"] * 2, self.max_backoff)
        status = state["status"]
        
        if fails >= self.max_failures:
            status = "paused"
            logger.warning(f"Source {source_name} hit {fails} consecutive block failures. Pausing.")
        
        self.update_state(source_name, {
            "status": status,
            "consecutive_failure_count": fails,
            "current_backoff_interval": new_backoff,
            "last_run_at": datetime.now(timezone.utc)
        })

    def record_drift(self, source_name: str, new_health_score: float) -> None:
        """Handle Structural Drift: Update health score without triggering backoff/pause."""
        self.update_state(source_name, {
            "selector_health_score": new_health_score,
            "last_run_at": datetime.now(timezone.utc)
        })
