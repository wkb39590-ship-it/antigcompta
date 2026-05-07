import os
from google import genai
from google.genai.errors import APIError

def test_models():
    api_key = "AIzaSyBqbTZgYSEKGXEITaDU40Jm2mCq1FrBtVU"
    client = genai.Client(api_key=api_key)
    
    # Large payload
    large_text = "Test API " * 1000
    
    models_to_test = [
        'gemini-2.0-flash-lite',
        'gemini-2.5-flash-lite',
        'gemini-flash-latest',
        'gemini-2.5-flash'
    ]
    
    for m in models_to_test:
        print(f"\n--- Testing {m} ---")
        try:
            response = client.models.generate_content(
                model=m,
                contents=large_text
            )
            print(f"SUCCESS with {m}")
        except APIError as e:
            print(f"FAILED {m}: {e.code} - {e.message}")
        except Exception as e:
            print(f"FAILED {m}: {type(e).__name__} - {e}")

if __name__ == "__main__":
    test_models()
