import re, json

with open(r"D:\Projet automobile\vente-auto-platform\backend\tests\avito_debug.html", encoding="utf-8") as f:
    html = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
data = json.loads(match.group(1))
ads = data["props"]["pageProps"]["componentProps"]["ads"]["ads"]

print(f"Total ads: {len(ads)}")
for idx, ad in enumerate(ads):
    title = ad.get("subject", "")
    price = ad.get("price", {})
    params = {p["key"]: p.get("value", "") for p in ad.get("params", {}).get("secondary", [])}
    mileage_val = params.get("mileage_exact", "N/A")
    mileage_type = type(mileage_val).__name__
    
    # Check brand parsing
    parts = title.split()
    brand = parts[0] if parts else "?"
    model = " ".join(parts[1:]) if len(parts) > 1 else ""
    
    print(f"\n--- Ad {idx+1} ---")
    print(f"  Title: {title[:80]}")
    print(f"  Brand: {brand}")
    print(f"  Price: {price.get('value')} ({type(price.get('value')).__name__})")
    print(f"  Mileage: {mileage_val} (type: {mileage_type})")
    print(f"  Params: {json.dumps(params, ensure_ascii=False)}")
    
    if idx >= 15:
        break
