
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_available_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: No GEMINI_API_KEY found in .env")
        return
    client = genai.Client(api_key=api_key)
    print("--- Available Models ---")
    try:
        # Use the correct SDK method to list models
        for m in client.models.list():
            print(f"- {m.name} (Supported: {m.supported_actions})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_available_models()
