import requests

try:
    res = requests.get('http://localhost:8000/api/vehicles/520475f0-2f8c-48ee-8d59-9e40650cb33b')
    print("Status:", res.status_code)
    print("Data:", res.json())
except Exception as e:
    print("Error:", e)
