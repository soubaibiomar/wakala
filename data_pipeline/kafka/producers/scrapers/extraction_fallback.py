import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class FallbackExtractor:
    @staticmethod
    def extract_text(elem, primary_selector: str, fallbacks: list = None, heuristic: str = None) -> Optional[str]:
        """
        Try extracting using primary selector, then fallbacks, then heuristic.
        """
        # 1. Primary selector
        if primary_selector:
            try:
                target = elem.select_one(primary_selector)
                if target:
                    return target.get_text(" ", strip=True)
            except Exception as e:
                logger.debug(f"Primary selector '{primary_selector}' failed: {e}")

        # 2. Fallbacks
        if fallbacks:
            for selector in fallbacks:
                try:
                    target = elem.select_one(selector)
                    if target:
                        return target.get_text(" ", strip=True)
                except Exception as e:
                    logger.debug(f"Fallback selector '{selector}' failed: {e}")

        # 3. Generic Heuristics
        if heuristic:
            text_content = elem.get_text(" ", strip=True)
            return FallbackExtractor._apply_heuristic(text_content, heuristic)

        return None
        
    @staticmethod
    def extract_attr(elem, primary_selector: str, attr: str, fallbacks: list = None) -> Optional[str]:
        """Extract an attribute from an element (like href)"""
        # 1. Primary
        if primary_selector:
            target = elem.select_one(primary_selector)
            if target and target.has_attr(attr):
                return target[attr]
                
        # 2. Fallbacks
        if fallbacks:
            for selector in fallbacks:
                target = elem.select_one(selector)
                if target and target.has_attr(attr):
                    return target[attr]
                    
        return None

    @staticmethod
    def _apply_heuristic(text: str, heuristic: str) -> Optional[str]:
        """Apply generic regex heuristic on raw text"""
        if not text:
            return None
            
        if heuristic == "price":
            # Match number + DH/MAD
            match = re.search(r'([\d\s\.,]+)\s*(?:DH|MAD|DHS|dirhams)', text, re.IGNORECASE)
            if match:
                return match.group(0)
        elif heuristic == "year":
            # Match 1990 - 2026
            match = re.search(r'\b(199\d|200\d|201\d|202[0-6])\b', text)
            if match:
                return match.group(1)
        elif heuristic == "mileage":
            # Match number + KM
            match = re.search(r'([\d\s\.,]+)\s*(?:km|kms)', text, re.IGNORECASE)
            if match:
                return match.group(0)
                
        return None
