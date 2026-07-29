import json
with open('wakala_architecture_complete_explique.excalidraw', 'r', encoding='utf-8') as f:
    data = json.load(f)

for e in data.get('elements', []):
    t = e.get('text', '')
    if 'Karim' in t or 'Ex' in t or 'Score Final' in t:
        t_clean = t.encode('ascii', 'ignore').decode('ascii').replace('\n', ' ')
        print(f"{e.get('type')}: X={e.get('x')}, Y={e.get('y')}, W={e.get('width')}, H={e.get('height')} -> {t_clean[:60]}...")
