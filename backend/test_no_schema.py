
import os
from google import genai
import json

api_key = "AIzaSyD4a5MerXj2lJAKZFKq1Ybd1aNuvbBLvs4"
client = genai.Client(api_key=api_key)

prompt = "Extrais les transactions de ce relevé bancaire au format JSON pur."

# Test avec une image simple
upload_dir = "uploads"
files = [f for f in os.listdir(upload_dir) if f.endswith(".jpg") or f.endswith(".png")]
if not files:
    print("No images found")
    exit()

test_file = os.path.join(upload_dir, files[0])
with open(test_file, "rb") as f:
    img_data = f.read()

try:
    print(f"Testing Gemini WITHOUT schema for {test_file}...")
    resp = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            "Extrait les transactions de cette image en JSON.",
            {"inline_data": {"mime_type": "image/jpeg", "data": img_data}}
        ],
        config={
            "temperature": 0.0,
        }
    )
    print("SUCCESS!")
    print(resp.text)
except Exception as e:
    print(f"FAILED: {e}")
