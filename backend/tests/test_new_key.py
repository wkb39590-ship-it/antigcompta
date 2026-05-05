import os
import json
from google import genai

# Test direct avec la NOUVELLE clé
api_key = "AIzaSyD4a5MerXj2lJAKZFKq1Ybd1aNuvbBLvs4"
client = genai.Client(api_key=api_key)

try:
    print(f"Test Gemini avec la clé ...fwoc")
    resp = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Bonjour, test d'extraction. Réponds OK."
    )
    print(f"Status: SUCCESS")
    print(f"Réponse: {resp.text}")
except Exception as e:
    print(f"Status: ERROR")
    print(f"Détails: {str(e)}")
