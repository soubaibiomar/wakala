import json
from pathlib import Path
from scrapers.avito_scraper import AvitoScraper

html = Path('tests/fixtures/scraped_html/avito_page1.html').read_text()
scraper = AvitoScraper()

print('Parsing Avito HTML...')
raw_listings = scraper._parse_listings_page(html, max_items=10)
print(f'Found {len(raw_listings)} raw listings')
for i, listing in enumerate(raw_listings):
    print(f'  Listing {i+1}: {listing.get("brand")} {listing.get("model")}')
    print(f'    Price: {listing.get("price")}')
    print(f'    City: {listing.get("city")}')
    print(f'    Year: {listing.get("year")}')
    print(f'    Fuel: {listing.get("fuel_type")}')