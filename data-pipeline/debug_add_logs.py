# Temporarily modify avito_scraper to add debug output
with open('data_pipeline/kafka/producers/scrapers/avito_scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add debug prints before the return in _parse_next_data
old_parse_next_data = """    def _parse_next_data(self, data: dict, max_items: int) -> List[Dict[str, Any]]:
        \"\"\"Parse the Next.js __NEXT_DATA__ JSON structure\"\"\"
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

        return listings"""

new_parse_next_data = """    def _parse_next_data(self, data: dict, max_items: int) -> List[Dict[str, Any]]:
        \"\"\"Parse the Next.js __NEXT_DATA__ JSON structure\"\"\"
        listings = []
        try:
            # Navigate to the ads array - structure may vary
            page_props = data.get('props', {}).get('pageProps', {})
            ads = page_props.get('ads', []) or page_props.get('initialAds', [])

            print(f\"[DEBUG] Found {len(ads)} ads in page_props\")
            print(f\"[DEBUG] page_props keys: {page_props.keys()}\")
            for ad in ads[:max_items]:
                print(f\"[DEBUG] Processing ad: {ad.get('title', 'No title')}\")
                listing = self._parse_ad_json(ad)
                print(f\"[DEBUG] Parsed listing: {listing.get('brand')} {listing.get('model') if listing.get('model') else 'N/A'}\")
                if listing:
                    listings.append(listing)
            print(f\"[DEBUG] Total listings: {len(listings)}\")

        except Exception as e:
            logger.error(f"Error parsing __NEXT_DATA__: {e}")

        return listings"""

content = content.replace(old_parse_next_data, new_parse_next_data)

# Also add debug before the return in _parse_ad_json
old_parse_ad_json = """            return raw_data
        except Exception as e:
            logger.error(f"Error parsing ad JSON: {e}")
            return None"""

new_parse_ad_json = """            print(f\"[DEBUG] Parsed ad JSON: brand={brand}, model={model}, year={year}, city={location}\")
            return raw_data
        except Exception as e:
            logger.error(f"Error parsing ad JSON: {e}")
            print(f\"[DEBUG] Error parsing ad: {e}\")
            return None"""

content = content.replace(old_parse_ad_json, new_parse_ad_json)

with open('data_pipeline/kafka/producers/scrapers/avito_scraper.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Debug statements added to avito_scraper.py")