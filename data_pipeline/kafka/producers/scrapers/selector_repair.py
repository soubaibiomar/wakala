import logging
from typing import Optional

from .llm_client import ask_cloud_llm
from .selector_review_queue import SelectorReviewQueue

logger = logging.getLogger(__name__)

class SelectorRepair:
    def __init__(self):
        self.queue = SelectorReviewQueue()

    def propose_repair(self, site: str, field: str, html_snippet: str) -> Optional[str]:
        """
        Handles Structural Drift by querying the configured cloud model
        based on the provided HTML snippet.
        Only called on branch (a) Structural Drift. NEVER on Active Block.
        """
        logger.info(f"Initiating selector self-repair for {site}.{field} (Structural Drift)")
        
        prompt = (
            f"The CSS selector for the field '{field}' on the site '{site}' has broken "
            f"due to structural drift. Below is a snippet of the current HTML for the page.\n\n"
            f"HTML Snippet:\n```html\n{html_snippet}\n```\n\n"
            f"Please analyze the HTML and provide a new, valid CSS selector that uniquely "
            f"targets the value for '{field}'. Output ONLY the CSS selector string. "
            f"Do not include any explanation, reasoning, or markdown formatting."
        )
        
        new_selector = ask_cloud_llm(prompt)
        
        if not new_selector:
            logger.error(f"Cloud model failed to propose a new selector for {site}.{field}")
            return None
            
        logger.info(f"Cloud model proposed new selector: {new_selector}")
        
        # Write to review queue (human validation required)
        self.queue.add_suggestion(
            site=site,
            field=field,
            new_selector=new_selector,
            confidence=0.8,  # Default heuristic confidence
            reasoning="Proposed by cloud-model self-repair due to structural drift.",
            example_value="Requires manual verification."
        )
        
        return new_selector
