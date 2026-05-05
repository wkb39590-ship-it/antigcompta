import os
from google import genai
import time

keys = [os.getenv("GEMINI_API_KEY"), os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2"), os.getenv("GEMINI_API_KEY_3")]
models_to_test = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

print("--- STARTING TESTS ---", flush=True)

for i, key in enumerate(keys):
    if not key: continue
    client = genai.Client(api_key=key)
    print(f"\n>>>> Testing Key {i} ({key[:10]}...)", flush=True)
    for m in models_to_test:
        time.sleep(1)
        try:
            resp = client.models.generate_content(
                model=m,
                contents="Dis bonjour"
            )
            print(f"[OK] {m} : {resp.text.strip()}", flush=True)
        except Exception as e:
            err_msg = str(e)
            if "NOT_FOUND" in err_msg:
                print(f"[FAIL] {m} : 404 NOT_FOUND", flush=True)
            elif "UNAVAILABLE" in err_msg:
                print(f"[FAIL] {m} : 503 UNAVAILABLE (Surchargé)", flush=True)
            elif "EXHAUSTED" in err_msg or "429" in err_msg:
                print(f"[FAIL] {m} : 429 QUOTA EXHAUSTED", flush=True)
            else:
                print(f"[FAIL] {m} : {err_msg}", flush=True)
