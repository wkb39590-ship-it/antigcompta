
import os
import sys
import json
import asyncio
from google import genai

# Setup path
os.chdir("/app")
sys.path.append("/app")

async def test_minimal():
    api_key = os.getenv("GEMINI_API_KEY")
    # HARDCODE THE MODEL from our confirmed models_list.txt
    model_name = "gemini-2.5-flash" 
    print(f"Testing with API_KEY: {api_key[:5]}...{api_key[-5:]}")
    print(f"Testing with Model: {model_name}")
    
    client = genai.Client(api_key=api_key)
    try:
        # Simple text test
        resp = client.models.generate_content(
            model=model_name,
            contents="Say hello"
        )
        print(f"Success! Gemini Response: {resp.text}")
    except Exception as e:
        print(f"--- FAILURE DETAIL ---")
        print(f"Type: {type(e)}")
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_minimal())
