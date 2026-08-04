import json

with open("Wakala-Archi.excalidraw", encoding="utf-8") as f:
    data = json.load(f)

texts = [e for e in data["elements"] if e["type"] == "text"]
for t in texts[:20]:
    print(f"X: {t['x']}, Y: {t['y']}, Text: {t['text'][:50].replace(chr(10), ' ')}")
