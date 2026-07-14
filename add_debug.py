# Add debug statements to avito_scraper
with open('data_pipeline/kafka/producers/scrapers/avito_scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add debug prints in _parse_next_data
content = content.replace(
    '''    def _parse_next_data(self, data: dict, max_items: int) -> List[Dict[str, Any]]:
        """Parse the Next.js __NEXT_DATA__ JSON structure"""
        listings = []
        try:
            # Navigate to the ads array - structure may vary
            page_props = data.get('props', {}).get('pageProps', {})
            ads = page_props.get('ads', []) or page_props.get('initialAds', [])

            for ad in ads[:max_items]:
                listing = self._parse_ad_json(ad)
                if listing:
                    listings.append(listing)

        except Exception as e:
            logger.error(f"Error parsing __NEXT_DATA__: {e}")

        return listings''',
    '''    def _parse_next_data(self, data: dict, max_items: int) -> List[Dict[str, Any]]:
        """Parse the Next.js __NEXT_DATA__ JSON structure"""
        listings = []
        try:
            # Navigate to the ads array - structure may vary
            page_props = data.get('props', {}).get('pageProps', {})
            ads = page_props.get('ads', []) or page_props.get('initialAds', [])

            print(f"[DEBUG] Found {len(ads)} ads in page_props")
            print(f"[DEBUG] page_props keys: {list(page_props.keys())}")
            for ad in ads[:max_items]:
                title = ad.get('title', 'No title')
                print(f"[DEBUG] Processing ad: {title[:50]}...")
                listing = self._parse_ad_json(ad)
                brand = listing.get('brand', 'N/A') if listing else 'N/A'
                model = listing.get('model', '') or ''
                print(f"[DEBUG] Parsed: {brand} {model}")
                if listing:
                    listings.append(listing)
            print(f"[DEBUG] Total listings collected: {len(listings)}")

        except Exception as e:
            logger.error(f"Error parsing __NEXT_DATA__: {e}")

        return listings'''
)

with open('data_pipeline/kafka/producers/scrapers/avito_scraper.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Debug statements added to avito_scraper.py")