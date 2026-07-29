import urllib.request

brands = [
    "Byd", "Mg", "Chery", "Geely", "Changan", "Dongfeng", "Haval", "Jac", 
    "Mazda", "Mitsubishi", "Mini", "Lexus", "Jaguar", "Maserati", "Baic", "Seres", "Omoda", "Jaecoo"
]

for brand in brands:
    b = brand.capitalize()
    urls = [
        f"https://www.wandaloo.com/imgs/logo-{b}-b.png",
        f"https://www.wandaloo.com/imgs/logo-{b}.png",
        f"https://www.wandaloo.com/imgs/logo-{brand.upper()}-b.png",
        f"https://www.wandaloo.com/imgs/logo-{brand.upper()}.png",
        f"https://www.wandaloo.com/imgs/logo-{b.lower()}-b.png",
        f"https://www.wandaloo.com/imgs/logo-{b.lower()}.png",
    ]
    found = False
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            res = urllib.request.urlopen(req)
            if res.status == 200:
                print(f"{brand} -> {url}")
                found = True
                break
        except Exception:
            pass
    if not found:
        print(f"{brand} -> NOT FOUND")
