import re, json

with open(r"D:\Projet automobile\vente-auto-platform\backend\tests\avito_debug.html", encoding="utf-8") as f:
    html = f.read()

# Extract __NEXT_DATA__
match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
if not match:
    match = re.search(r'__NEXT_DATA__.*?type="application/json">(.*?)</script>', html, re.DOTALL)

if match:
    data = json.loads(match.group(1))
    print(f"Top keys: {list(data.keys())}")
    if "props" in data:
        props = data["props"]
        print(f"\nProps keys: {list(props.keys())}")
        if "pageProps" in props:
            pp = props["pageProps"]
            print(f"\npageProps keys: {list(pp.keys())}")
            # Look for ads/listings data
            for key, val in pp.items():
                if isinstance(val, (list, dict)):
                    print(f"\n  {key}: {type(val).__name__}")
                    if isinstance(val, dict):
                        print(f"  subkeys: {list(val.keys())[:10]}")
                        # Look for ads in subkeys
                        for sk, sv in val.items():
                            if isinstance(sv, list) and len(sv) > 0:
                                print(f"    {sk}: list[{len(sv)}]")
                                if len(sv) > 0:
                                    print(f"    sample: {json.dumps(sv[0], ensure_ascii=False)[:500]}")
                            elif isinstance(sv, dict):
                                print(f"    {sk}: dict with keys {list(sv.keys())[:10]}")
                    elif isinstance(val, list) and len(val) > 0:
                        print(f"  first item: {json.dumps(val[0], ensure_ascii=False)[:500]}")
else:
    print("__NEXT_DATA__ not found")
