import httpx, json
resp = httpx.get("http://localhost:8000/api/vehicles/")
d = resp.json()
print(f"Total: {d['total']} vehicules")
for v in d["items"][:10]:
    print(f'  {v["brand"]} {v["model"]} ({v["year"]}) - {v["price"]:,.0f} MAD - {v["city"]}')
