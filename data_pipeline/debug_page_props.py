import json
from pathlib import Path
from bs4 import BeautifulSoup

html = Path('tests/fixtures/scraped_html/avito_page1.html').read_text()
soup = BeautifulSoup(html, 'html.parser')

next_data_script = soup.find('script', id='__NEXT_DATA__')
if next_data_script:
    data = json.loads(next_data_script.string)
    page_props = data.get('props', {}).get('pageProps', {})
    ads = page_props.get('ads', []) or page_props.get('initialAds', [])
    print(f'page_props keys: {page_props.keys()}')
    print(f'ads key exists: {"ads" in page_props}')
    print(f'initialAds key exists: {"initialAds" in page_props}')
    print(f"ads value: {page_props.get('ads')}")
    print(f"initialAds value: {page_props.get('initialAds')}")
    print(f"ads is empty: {page_props.get('ads') == []}")
    print(f"total items: {len(ads)}")