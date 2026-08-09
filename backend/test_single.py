import json
import urllib.request
import time

prompt = "bghit nchri tomobila"
print(f"Testing prompt: {prompt}")
data = json.dumps({"message": prompt, "history": []}).encode('utf-8')
req = urllib.request.Request(
    "http://localhost:8000/api/v1/ai/chat",
    data=data,
    headers={"Content-Type": "application/json"}
)
start = time.time()
resp = urllib.request.urlopen(req, timeout=120)
print("Response connected, reading stream...")
full_resp = ""
for line in resp:
    dec = line.decode('utf-8')
    if dec.startswith('data: '):
        token = dec[6:]
        full_resp += token
        print(token, end='', flush=True)

print(f"\n\nTotal time: {time.time() - start:.2f}s")
