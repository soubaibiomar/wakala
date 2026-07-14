import re, json

with open(r"D:\Projet automobile\vente-auto-platform\backend\tests\avito_debug.html", encoding="utf-8") as f:
    html = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
data = json.loads(match.group(1))
ads_data = data["props"]["pageProps"]["componentProps"]["ads"]["ads"]

print(f"Total ads: {len(ads_data)}")
print(f"Type: {type(ads_data).__name__}")

if isinstance(ads_data, list):
    for idx, ad in enumerate(ads_data[:3]):
        print(f"\n--- Ad {idx+1} ---")
        print(json.dumps(ad, ensure_ascii=False, indent=2)[:2000])
elif isinstance(ads_data, dict):
    for key, val in ads_data.items():
        print(f"\nKey: {key} ({type(val).__name__})")
        if isinstance(val, list) and len(val) > 0:
            print(f"  Sample: {json.dumps(val[0], ensure_ascii=False)[:1000]}")

# Also check initialReduxState
redux = data["props"]["pageProps"]["initialReduxState"]
if "ad" in redux and "search" in redux["ad"]:
    search = redux["ad"]["search"]
    print(f"\n\nRedux search keys: {list(search.keys()) if isinstance(search, dict) else 'N/A'}")
    if isinstance(search, dict):
        for k, v in search.items():
            if isinstance(v, list) and len(v) > 0:
                print(f"  {k}: list[{len(v)}]")
                print(f"  Sample: {json.dumps(v[0], ensure_ascii=False)[:1000]}")
