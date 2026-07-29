import json
with open('wakala_architecture_complete_explique.excalidraw', 'r', encoding='utf-8') as f:
    data = json.load(f)

for e in data.get('elements', []):
    x = e.get('x', 0)
    y = e.get('y', 0)
    if x > 1500 and 800 < y <= 1100:
        t = e.get('text', '').replace('\n', ' ') if e.get('type') == 'text' else ''
        t = t.encode('ascii', 'ignore').decode('ascii')
        print(f"{e.get('type')} Y={int(y)}: {t[:40]}")
