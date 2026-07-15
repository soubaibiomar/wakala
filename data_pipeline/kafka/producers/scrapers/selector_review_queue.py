import json
import logging
import uuid
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SelectorReviewQueue:
    def __init__(self, queue_file: str = "pending_selectors.json"):
        self.queue_path = Path(__file__).parent / queue_file
        self.selectors_dir = Path(__file__).parent / "selectors"

    def _load_queue(self) -> List[Dict[str, Any]]:
        if not self.queue_path.exists():
            return []
        try:
            with open(self.queue_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load selector review queue: {e}")
            return []

    def _save_queue(self, queue: List[Dict[str, Any]]) -> None:
        try:
            with open(self.queue_path, "w", encoding="utf-8") as f:
                json.dump(queue, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save selector review queue: {e}")

    def add_suggestion(self, site: str, field: str, new_selector: str, confidence: float, reasoning: str, example_value: str) -> str:
        """Adds a new suggestion from the LLM to the queue."""
        queue = self._load_queue()
        
        # Check if identical suggestion already exists
        for item in queue:
            if item["site"] == site and item["field"] == field and item["new_selector"] == new_selector:
                logger.info(f"Suggestion for {site}.{field} -> {new_selector} already in queue.")
                return item["id"]
                
        suggestion_id = str(uuid.uuid4())
        suggestion = {
            "id": suggestion_id,
            "site": site,
            "field": field,
            "new_selector": new_selector,
            "confidence": confidence,
            "reasoning": reasoning,
            "example_value": example_value,
            "status": "pending",
            "created_at": __import__('datetime').datetime.utcnow().isoformat()
        }
        
        queue.append(suggestion)
        self._save_queue(queue)
        logger.info(f"Added new selector suggestion to queue: {suggestion_id}")
        return suggestion_id

    def get_pending(self) -> List[Dict[str, Any]]:
        """Returns all pending suggestions."""
        queue = self._load_queue()
        return [item for item in queue if item["status"] == "pending"]

    def reject_suggestion(self, suggestion_id: str) -> bool:
        """Marks a suggestion as rejected."""
        queue = self._load_queue()
        for item in queue:
            if item["id"] == suggestion_id:
                item["status"] = "rejected"
                self._save_queue(queue)
                return True
        return False

    def approve_suggestion(self, suggestion_id: str, is_fallback: bool = False) -> bool:
        """Applies the suggestion to the YAML file and marks as approved."""
        queue = self._load_queue()
        target_suggestion = next((item for item in queue if item["id"] == suggestion_id), None)
        
        if not target_suggestion:
            return False
            
        site = target_suggestion["site"]
        field = target_suggestion["field"]
        new_selector = target_suggestion["new_selector"]
        
        yaml_path = self.selectors_dir / f"{site}_selectors.yaml"
        if not yaml_path.exists():
            logger.error(f"YAML file {yaml_path} not found.")
            return False
            
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                
            if is_fallback:
                # Add to fallback_fields
                if "fallback_fields" not in data:
                    data["fallback_fields"] = {}
                if field not in data["fallback_fields"]:
                    data["fallback_fields"][field] = []
                if new_selector not in data["fallback_fields"][field]:
                    data["fallback_fields"][field].insert(0, new_selector)
            else:
                # Replace primary field
                if "fields" not in data:
                    data["fields"] = {}
                data["fields"][field] = new_selector
                
            with open(yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)
                
            target_suggestion["status"] = "approved"
            self._save_queue(queue)
            logger.info(f"Successfully applied new selector for {site}.{field}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update YAML file: {e}")
            return False
