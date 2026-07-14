from scrapers.avito_scraper import AvitoScraper
from pathlib import Path

html = Path('tests/fixtures/scraped_html/avito_page1.html').read_text()
scraper = AvitoScraper()
raw = scraper._parse_listings_page(html, max_items=10)
print(f'Found {len(raw)} listings')
for r in raw:
    print(f'  - {r["brand"]} {r["model"]} - {r["price"]} - {r["city"]}')