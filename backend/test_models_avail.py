import os
from google import genai
import time

keys = [os.getenv("GEMINI_API_KEY"), os.getenv("GEMINI_API_KEY_1")]
models_to_test = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

for i, key in enumerate(keys):
    if not key: continue
    client = genai.Client(api_key=key)
    print(f"\n--- Testing Key {i} ---")
    for m in models_to_test:
        print(f"Testing model {m}...")
        try:
            resp = client.models.generate_content(
                model=m,
                contents="Dis bonjour"
            )
            print(f"Success with {m}: {resp.text.strip()}")
        except Exception as e:
            print(f"Failed with {m}: {e}")
        time.sleep(2)
