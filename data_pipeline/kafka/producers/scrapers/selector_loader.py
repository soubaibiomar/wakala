import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SelectorLoader:
    def __init__(self, selectors_dir: Path = None):
        if selectors_dir is None:
            self.selectors_dir = Path(__file__).parent / "selectors"
        else:
            self.selectors_dir = selectors_dir
            
        self._cache = {}

    def load(self, site: str) -> Dict[str, Any]:
        """Load selectors for a site, with caching"""
        if site in self._cache:
            return self._cache[site]

        filepath = self.selectors_dir / f"{site}_selectors.yaml"
        if not filepath.exists():
            logger.error(f"Selector file not found: {filepath}")
            return {}

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self._cache[site] = data
                return data
        except Exception as e:
            logger.error(f"Failed to load selectors for {site}: {e}")
            return {}
