import time
import random
import requests

class AntiDetectionSession:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        })

    def get(self, url: str, delay: int = 2) -> requests.Response:
        # Délai aléatoire pour simuler un humain
        time.sleep(delay + random.uniform(0.5, 1.5))
        return self.session.get(url, timeout=15)
