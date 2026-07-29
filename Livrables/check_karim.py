import json
import glob

for fname in glob.glob('*.excalidraw*'):
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                continue
            has_karim = any('karim' in e.get('text', '').lower() for e in data.get('elements', []) if e.get('type') == 'text')
            print(f'{fname}: size={len(data.get("elements", []))} elements, has_karim={has_karim}')
    except Exception as e:
        print(f'{fname}: Not a valid JSON ({e})')
