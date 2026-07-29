import random
import time
import requests
import cloudscraper
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
]

class ScraperHTTPClient:
    """
    A robust HTTP client for scraping. Handles rotating user-agents,
    automatic retries with backoff, polite delays, and bypasses anti-bots using CloudScraper.
    """
    
    def __init__(self, polite_delay_min: float = 1.0, polite_delay_max: float = 3.0):
        # Use cloudscraper to bypass anti-bot protections like Cloudflare
        self.session = cloudscraper.create_scraper(browser='chrome')
        self.polite_delay_min = polite_delay_min
        self.polite_delay_max = polite_delay_max
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Send a GET request with a randomized user-agent and a polite delay.
        """
        # Polite delay
        delay = random.uniform(self.polite_delay_min, self.polite_delay_max)
        time.sleep(delay)
        
        # Rotate UA
        headers = kwargs.get('headers', {})
        if 'User-Agent' not in headers:
            headers['User-Agent'] = random.choice(USER_AGENTS)
        kwargs['headers'] = headers
        
        # Default timeout
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 15
            
        return self.session.get(url, **kwargs)
