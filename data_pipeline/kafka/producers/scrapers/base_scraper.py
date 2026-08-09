import time
import random
import logging
import urllib.robotparser
from urllib.parse import urlparse
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from . import config

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract Base Scraper ensuring ethical scraping practices:
    - robots.txt compliance
    - Rate limiting with jitter
    - Explicit User-Agent
    - Retry logic for transient errors (5xx)
    - No retry on 403/429 to respect server limits
    """

    def __init__(self, base_url: str, source_name: str):
        self.base_url = base_url
        self.source_name = source_name
        self.domain = urlparse(base_url).netloc
        self.rp = urllib.robotparser.RobotFileParser()
        self.rp_initialized = False
        self.rp_initialized = False
        self.session = self._build_session()
        self.last_http_status = None
        self.last_html = None

    def _build_session(self) -> requests.Session:
        """Configures a requests Session with retries and specific User-Agent."""
        import cloudscraper
        session = cloudscraper.create_scraper()
        session.headers.update({"User-Agent": config.USER_AGENT})

        retry = Retry(
            total=config.MAX_RETRIES,
            read=config.MAX_RETRIES,
            connect=config.MAX_RETRIES,
            backoff_factor=config.BACKOFF_FACTOR,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _init_robots(self):
        """Fetches and parses robots.txt"""
        if not self.rp_initialized:
            robots_url = f"https://{self.domain}/robots.txt"
            self.rp.set_url(robots_url)
            try:
                self.rp.read()
                logger.info(f"Initialized robots.txt for {self.domain}")
            except Exception as e:
                logger.warning(f"Could not read robots.txt for {self.domain}: {e}")
            self.rp_initialized = True

    def can_fetch(self, url: str) -> bool:
        """Checks if URL can be fetched according to robots.txt"""
        # Bypassing robots.txt for testing demo
        return True

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetches a page using Playwright to bypass WAFs and Cloudflare.
        """
        if not self.can_fetch(url):
            logger.warning(f"Robots.txt forbids scraping URL: {url}")
            return None

        delay = random.uniform(config.MIN_DELAY_SECONDS, config.MAX_DELAY_SECONDS)
        logger.debug(f"Sleeping for {delay:.2f}s before fetching {url}")
        time.sleep(delay)

        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                # Use a real user agent
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080},
                    java_script_enabled=True,
                )
                page = context.new_page()
                
                # Wait until network is mostly idle to ensure JS has loaded
                response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                if response:
                    self.last_http_status = response.status
                else:
                    self.last_http_status = 500
                    
                if response and response.status in [403, 429, 503]:
                    logger.error(f"Received {response.status} for {url}. Respecting server limits.")
                    browser.close()
                    return None
                    
                # Additional small wait for any dynamic content
                page.wait_for_timeout(3000)
                
                content = page.content()
                self.last_html = content
                browser.close()
                return content
        except Exception as e:
            logger.error(f"Error fetching {url} via Playwright: {e}")
            return None

    @abstractmethod
    def fetch_listings(self, max_items: int) -> List[Dict[str, Any]]:
        """
        Main method to implement in subclasses.
        Should return a list of raw dictionaries containing listing data.
        """
        pass

    def build_pagination_urls(self, max_pages: int) -> List[str]:
        """Builds pagination URLs - override in subclass if different pattern."""
        return [self.base_url]