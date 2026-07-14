from abc import ABC, abstractmethod
from typing import Optional


class BaseScraper(ABC):
    SOURCE_NAME: str

    @abstractmethod
    def fetch_page(self, url: str, page: int) -> list[dict]: ...
