import json
from pathlib import Path
from bs4 import BeautifulSoup

html = Path('tests/fixtures/scraped_html/avito_page1.html').read_text()
soup = BeautifulSoup(html, 'html.parser')

# Check if we can find the script tag
next_data_script = soup.find('script', id='__NEXT_DATA__')
if next_data_script:
    print('Found script tag')
    print('Type:', next_data_script.get('type'))
    print('Has string:', hasattr(next_data_script, 'string'))
    if hasattr(next_data_script, 'string'):
        print('String length:', len(next_data_script.string) if next_data_script.string else 0)
        print('String preview:', next_data_script.string[:200] if next_data_script.string else 'None')

        # Try to parse
        try:
            data = json.loads(next_data_script.string)
            page_props = data.get('props', {}).get('pageProps', {})
            ads = page_props.get('ads', []) or page_props.get('initialAds', [])
            print(f'Found {len(ads)} ads in __NEXT_DATA__')
            for i, ad in enumerate(ads):
                print(f'  Ad {i+1}: {ad.get("title", "No title")}')
        except Exception as e:
            print(f'Error parsing JSON: {e}')
            import traceback
            traceback.print_exc()
else:
    print('ERROR: __NEXT_DATA__ script tag not found!')