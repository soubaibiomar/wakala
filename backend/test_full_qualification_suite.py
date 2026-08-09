import json
import urllib.request
import time

def call_chat(message: str, history=None):
    if history is None:
        history = []
    data = json.dumps({"message": message, "history": history}).encode('utf-8')
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/ai/chat",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    start_t = time.time()
    resp = urllib.request.urlopen(req, timeout=120)
    full_text = ""
    for chunk in resp:
        dec = chunk.decode('utf-8')
        full_text += dec
        print(dec, end='', flush=True)
    print(f"\n[Took {time.time() - start_t:.1f}s]")
    return full_text.strip()

def run_tests():
    print("==================================================================")
    print("TEST 1: Darija Exploratory Query (Should ask qualifying questions, NO car cards)")
    print("==================================================================")
    msg1 = "Salam, bghit nchri chi tomobila"
    print(f"User: {msg1}\nAI Streaming: ")
    res1 = call_chat(msg1)
    print(f"\nAI Response:\n{res1}\n")
    assert "CAR_RECOMMENDATION" not in res1, "ERROR: CAR_RECOMMENDATION found in exploratory query!"
    print(">>> SUCCESS: No premature vehicle recommendation cards. Asked diagnostic questions!")

    print("\n==================================================================")
    print("TEST 2: Darija Follow-up with Qualified Criteria (Should recommend matching cars)")
    print("==================================================================")
    msg2 = "3ndi budget d 110 000 dh w baghiha diesel l mdina w safar"
    print(f"User: {msg2}\nAI Streaming: ")
    history = [
        {"role": "user", "content": msg1},
        {"role": "assistant", "content": res1}
    ]
    res2 = call_chat(msg2, history=history)
    print(f"\nAI Response:\n{res2}\n")
    print(">>> SUCCESS: Follow-up response with qualified recommendations received!")

    print("\n==================================================================")
    print("TEST 3: French Exploratory Query (Should ask qualifying questions, NO car cards)")
    print("==================================================================")
    msg3 = "Bonjour, je cherche a acheter une voiture"
    print(f"User: {msg3}\nAI Streaming: ")
    res3 = call_chat(msg3)
    print(f"\nAI Response:\n{res3}\n")
    assert "CAR_RECOMMENDATION" not in res3, "ERROR: CAR_RECOMMENDATION found in French exploratory query!"
    print(">>> SUCCESS: French qualification questions asked without premature cards!")

if __name__ == "__main__":
    run_tests()
