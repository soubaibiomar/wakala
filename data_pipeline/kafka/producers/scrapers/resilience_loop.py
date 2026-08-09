import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from .source_state import SourceStateManager
from .selector_repair import SelectorRepair

logger = logging.getLogger(__name__)

class ResilienceLoop:
    def __init__(self):
        self.state_manager = SourceStateManager()
        self.repair_engine = SelectorRepair()

    def should_run(self, source_name: str, normal_interval_hours: float) -> bool:
        """
        CYCLE STEP 1: DETECT.
        Checks if the source should be skipped due to pause or backoff.
        """
        state = self.state_manager.get_state(source_name)
        status = state["status"]
        last_run = state.get("last_run_at")
        backoff_sec = state.get("current_backoff_interval", 3600)
        
        # Always run if never run before
        if not last_run:
            return True
            
        now = datetime.now(timezone.utc)
        elapsed_sec = (now - last_run).total_seconds()
        
        if status == "paused":
            # Check at reduced frequency (e.g. daily, 86400 seconds)
            if elapsed_sec < 86400:
                logger.info(f"Skipping {source_name}: PAUSED due to blocks. Next daily check in {(86400 - elapsed_sec)/3600:.1f}h")
                return False
            else:
                logger.info(f"Running daily block re-check for paused source: {source_name}")
                return True
                
        # If active or degraded, enforce normal interval OR backoff
        required_interval = max(normal_interval_hours * 3600, backoff_sec)
        if elapsed_sec < required_interval:
            logger.debug(f"Skipping {source_name}: inside interval/backoff window.")
            return False
            
        return True

    def evaluate_scrape(self, source_name: str, raw_listings: List[Dict[str, Any]], http_status: Optional[int], html_snippet: Optional[str], failed_fields: List[str] = None):
        """
        CYCLE STEP 3: EVALUATE.
        Classify exactly into (a) Structural Drift, (b) Active Block, (c) Success.
        """
        failed_fields = failed_fields or []
        
        # Branch (b): ACTIVE BLOCK
        if http_status in [403, 429, 503] or (raw_listings == [] and http_status != 200):
            logger.warning(f"[{source_name}] Branch (b) ACTIVE BLOCK detected. HTTP {http_status}")
            self.state_manager.record_block_failure(source_name)
            return

        # Branch (a): STRUCTURAL DRIFT
        # 200 OK, but extraction failed for specific required fields on many listings,
        # or we got 0 listings despite 200 OK (selectors might be completely broken)
        is_drift = False
        if http_status == 200:
            if not raw_listings and html_snippet:
                is_drift = True
                failed_fields.append("listing_card")
            elif failed_fields and html_snippet:
                is_drift = True
                
        if is_drift:
            logger.warning(f"[{source_name}] Branch (a) STRUCTURAL DRIFT detected. Failed fields: {failed_fields}")
            # Do NOT backoff/pause for drift! Just update health score and invoke Ollama repair.
            state = self.state_manager.get_state(source_name)
            new_health = max(0, state["selector_health_score"] - 10)
            self.state_manager.record_drift(source_name, new_health)
            
            for field in failed_fields:
                self.repair_engine.propose_repair(source_name, field, html_snippet)
            return

        # Branch (c): SUCCESS
        if raw_listings and not failed_fields:
            logger.info(f"[{source_name}] Branch (c) SUCCESS detected.")
            self.state_manager.record_success(source_name)
            return
