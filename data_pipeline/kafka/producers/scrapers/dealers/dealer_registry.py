import os
import yaml
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DealerRegistry:
    """
    Parses and loads the declarative dealer configurations from dealers.yaml.
    Provides the list of active dealers to the orchestrator.
    """
    def __init__(self, registry_file: str = None):
        if registry_file is None:
            # Default to the dealers.yaml in the same directory under registry/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            registry_file = os.path.join(current_dir, "registry", "dealers.yaml")
        
        self.registry_file = registry_file
        self.dealers = self._load_dealers()

    def _load_dealers(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.registry_file):
            logger.error(f"Dealer registry file not found at {self.registry_file}")
            return []
            
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if not data or 'dealers' not in data:
                logger.warning(f"No dealers found or invalid format in {self.registry_file}")
                return []
                
            return data.get('dealers', [])
        except Exception as e:
            logger.error(f"Failed to load dealer registry: {e}")
            return []

    def get_active_dealers(self) -> List[Dict[str, Any]]:
        """Returns only the dealers that are marked as active: true."""
        return [dealer for dealer in self.dealers if dealer.get("active", False)]

    def get_all_dealers(self) -> List[Dict[str, Any]]:
        """Returns all dealers, regardless of active status."""
        return self.dealers
