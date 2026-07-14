import re, json

with open(r"D:\Projet automobile\vente-auto-platform\backend\tests\avito_debug.html", encoding="utf-8") as f:
    html = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
data = json.loads(match.group(1))
ads = data["props"]["pageProps"]["componentProps"]["ads"]["ads"]

for idx, ad in enumerate(ads[:2]):
    print(f"\n=== Ad {idx+1}: {ad['subject']} ===")
    print(f"Price: {ad['price']['value']} {ad['price']['currency']}")
    print(f"Seller: {ad['seller']['name']} ({ad['seller']['type']})")
    
    if "params" in ad:
        for section, items in ad["params"].items():
            print(f"\n  [{section}]")
            for item in items:
                if isinstance(item, dict):
                    key = item.get("key", item.get("name", "?"))
                    val = item.get("value", item.get("label", "?"))
                    print(f"    {key}: {val}")
                else:
                    print(f"    {item}")
    
    # Also print any other fields
    print(f"\n  Other ad fields:")
    for k, v in ad.items():
        if k not in ("id", "listId", "subject", "description", "seller", "price", 
                     "monthlyPayment", "oldPrice", "defaultImage", "images", "videos",
                     "params", "category", "adType", "hasShipping", "isEcommerce"):
            val_str = str(v)[:80]
            print(f"    {k}: {val_str}")
