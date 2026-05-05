
import os
import sys
from google import genai

# Setup path
os.chdir("/app")
sys.path.append("/app")

async def list_available_models():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    print("--- Available Models ---")
    try:
        # Use the correct SDK method to list models
        for m in client.models.list():
            print(f"- {m.name} (Supported: {m.supported_actions})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(list_available_models())
