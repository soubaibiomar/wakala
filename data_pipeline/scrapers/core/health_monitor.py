import os
import json
import logging
from datetime import datetime
from typing import List
from models.listing import Listing

logger = logging.getLogger(__name__)

class ScraperHealthMonitor:
    def __init__(self, log_file: str = "scraper_health.log"):
        self.log_file = log_file

    def _log_health_issue(self, site: str, issue: str, details: dict):
        """
        Write a clear entry to scraper_health.log for human review.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "site": site,
            "issue": issue,
            "details": details
        }
        
        mode = "a" if os.path.exists(self.log_file) else "w"
        with open(self.log_file, mode, encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            
        logger.warning(f"HEALTH ALERT [{site}]: {issue} - Check {self.log_file}")

    def evaluate_run(self, site_name: str, listings: List[Listing], expected_min_count: int = 5):
        """
        Evaluate the results of a scraper run against a baseline.
        If the run fails health checks, it writes to the health log.
        """
        total = len(listings)
        
        # Check 1: Zero or extremely low volume
        if total < expected_min_count:
            self._log_health_issue(
                site=site_name,
                issue="Low or zero listing volume",
                details={"found": total, "expected_min": expected_min_count}
            )
            if total == 0:
                return False # Complete failure

        # Check 2: Missing descriptions or images (markup change indicator)
        if total > 0 and hasattr(listings[0], 'description'):
            missing_desc_count = sum(1 for l in listings if not getattr(l, 'description', None) or len(getattr(l, 'description', '').strip()) < 5)
            missing_img_count = sum(1 for l in listings if getattr(l, 'image_count', 0) == 0)
            
            desc_fail_rate = missing_desc_count / total
            img_fail_rate = missing_img_count / total
            
            if desc_fail_rate > 0.5:
                self._log_health_issue(
                    site=site_name,
                    issue="High rate of missing descriptions",
                    details={"missing": missing_desc_count, "total": total, "rate": desc_fail_rate}
                )
                
            if img_fail_rate > 0.8:
                self._log_health_issue(
                    site=site_name,
                    issue="High rate of missing images (Gallery selector broken?)",
                    details={"missing": missing_img_count, "total": total, "rate": img_fail_rate}
                )
            
        return True
