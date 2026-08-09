import json
import urllib.request
import time

def test_chat(prompt, label):
    print(f"\n==================================================")
    print(f"=== TEST: {label} ===")
    print(f"Prompt: {prompt}")
    data = json.dumps({"message": prompt, "history": []}).encode('utf-8')
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/ai/chat",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    start_t = time.time()
    try:
        resp = urllib.request.urlopen(req, timeout=180)
        full_text = ""
        for line in resp:
            decoded = line.decode('utf-8')
            if decoded.startswith('data: '):
                token = decoded[6:]
                full_text += token
                print(token, end='', flush=True)
        print(f"\n[Duration: {time.time() - start_t:.1f}s]")
        return full_text
    except Exception as e:
        print(f"\nError: {e}")
        return None

if __name__ == "__main__":
    # Test 1: Exploratory query in Darija (Latin)
    test_chat("bghit nchri tomobila", "Exploratory Darija Latin")
    
    # Test 2: Exploratory query in French
    test_chat("Je cherche a acheter une voiture", "Exploratory French")
