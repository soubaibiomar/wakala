import os
import sys
import logging
import json
import importlib
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

OPENROUTER_MODELS = [
    "nvidia/nemotron-3.5-lightning:free",
    "google/gemma-4-31b-it:free",
    "openrouter/free",
]
from langchain_core.messages import SystemMessage, HumanMessage

from .selector_review_queue import SelectorReviewQueue

# Add the root directory to sys.path so we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../..")))

load_dotenv()

logger = logging.getLogger(__name__)

class SelectorRegenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            model=os.getenv("OPENROUTER_MODEL", ""),
            extra_body={"models": OPENROUTER_MODELS},
            temperature=0.1
        )
        self.review_queue = SelectorReviewQueue()

    def regenerate_selectors(self, site: str, failing_fields: List[str]) -> None:
        """
        Attempts to find new CSS selectors for the failing fields by analyzing
        a sample HTML snippet with an LLM.
        """
        if not self.llm:
            logger.error("Cannot regenerate selectors: LLM not initialized.")
            return

        logger.info(f"Triggered selector regeneration for {site}, fields: {failing_fields}")

        # 1. Dynamically load the scraper
        scraper_class_name = f"{site.capitalize()}Scraper"
        module_name = f"data_pipeline.kafka.producers.scrapers.{site}_scraper"
        
        try:
            module = importlib.import_module(module_name)
            scraper_class = getattr(module, scraper_class_name)
            scraper = scraper_class()
        except Exception as e:
            logger.error(f"Failed to load scraper for {site}: {e}")
            return

        # 2. Fetch a sample page
        # We only fetch 1 page to minimize requests
        pages = scraper.build_pagination_urls(1)
        if not pages:
            return
            
        html = scraper.fetch_page(pages[0])
        if not html:
            logger.error(f"Failed to fetch sample HTML for {site} regeneration.")
            return

        # 3. Extract a meaningful snippet to send to the LLM
        # We don't want to send the entire page (too many tokens).
        # We try to find a repeating element that likely represents a listing.
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to find common listing containers
        snippet = ""
        possible_containers = soup.select("article, div.card, div[class*='item'], div[class*='ad']")
        if possible_containers:
            # Take the first one that has an anchor tag with an href
            for container in possible_containers:
                if container.select_one("a[href]"):
                    # Limit the snippet size to ~4000 characters just in case
                    snippet = container.prettify()[:4000]
                    break
        
        if not snippet:
            # Fallback: just send the body but heavily truncated
            body = soup.find('body')
            snippet = body.prettify()[:4000] if body else html[:4000]

        # 4. Ask the LLM for each failing field
        for field in failing_fields:
            self._ask_llm_for_selector(site, field, snippet)

    def _ask_llm_for_selector(self, site: str, field: str, html_snippet: str) -> None:
        prompt = f"""
        You are an expert web scraper and CSS selector engineer.
        Our web scraper for the site '{site}' has stopped working for the field '{field}'.
        
        Here is a snippet of the HTML for a single car listing card:
        ```html
        {html_snippet}
        ```
        
        Your task is to analyze the HTML and provide the BEST and most ROBUST CSS selector to extract the '{field}'.
        
        Guidelines:
        - If the field is 'price', look for numbers formatted as prices (e.g., 100 000 DH, MAD, etc.).
        - If the field is 'title', look for headings (h1, h2, h3) or links containing car brand names.
        - The selector should be specific enough to get the value, but generic enough to apply to other similar cards.
        
        Return your answer as a raw JSON object (NO Markdown, NO formatting, just JSON) with the following structure:
        {{
            "new_selector": ".example-class > h3",
            "confidence": 0.95,
            "reasoning": "Brief explanation of why this selector works",
            "example_value": "The text value that this selector would extract from the snippet"
        }}
        """

        try:
            messages = [
                SystemMessage(content="You are a JSON-only API. You must output valid JSON without any markdown formatting or wrapper."),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # Clean up potential markdown formatting from the LLM
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
                
            result = json.loads(content)
            
            # Add to review queue
            self.review_queue.add_suggestion(
                site=site,
                field=field,
                new_selector=result.get("new_selector"),
                confidence=result.get("confidence", 0.0),
                reasoning=result.get("reasoning", "No reasoning provided"),
                example_value=result.get("example_value", "N/A")
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON for {site}.{field}: {response.content}")
        except Exception as e:
            logger.error(f"Error during LLM selector regeneration for {site}.{field}: {e}")

# Example usage (can be removed in production)
if __name__ == "__main__":
    regenerator = SelectorRegenerator()
    # regenerator.regenerate_selectors("moteur", ["price"])
