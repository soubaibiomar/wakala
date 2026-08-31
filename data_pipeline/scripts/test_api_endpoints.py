import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_api():
    try:
        with urllib.request.urlopen('http://localhost:8000/api/v1/new-cars/brands') as resp:
            brands = json.loads(resp.read().decode('utf-8'))
            print(f'✅ Brands endpoint: {len(brands)} brands')

        with urllib.request.urlopen('http://localhost:8000/api/v1/new-cars/models') as resp:
            models = json.loads(resp.read().decode('utf-8'))
            print(f'✅ Models endpoint: {len(models)} models')

        with urllib.request.urlopen('http://localhost:8000/api/vehicles/?limit=5') as resp:
            veh_data = json.loads(resp.read().decode('utf-8'))
            items = veh_data.get('items', veh_data if isinstance(veh_data, list) else [])
            total = veh_data.get('total', len(items)) if isinstance(veh_data, dict) else len(items)
            print(f'✅ /api/vehicles/ endpoint: {total} total vehicles')
            for v in items[:3]:
                print(f"   - {v['brand']} {v['model']} ({v.get('price')} MAD)")
    except Exception as e:
        print(f'❌ API Error: {e}')

if __name__ == '__main__':
    test_api()
