import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
for m in client.models.list():
    if getattr(m, 'supported_generation_methods', None) and 'generateContent' in m.supported_generation_methods:
        print(m.name)
