import os
import sys
import json
import base64
from google import genai
from services.pdf_utils import pdf_to_png_images_bytes

# Diagnostic script inside container
api_key = os.getenv("GEMINI_API_KEY_1")
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

print(f"--- DIAGNOSTIC GEMINI ---")
print(f"Key: {api_key[:10]}...")
print(f"Model selected: {model}")

# Essayer d'extraire la derniere facture (id 47 par exemple)
facture_id = 47
facture_path = "/app/uploads/EL OUJDI.pdf" # A adapter si possible

if not os.path.exists(facture_path):
    print(f"Fichier non trouve: {facture_path}. Liste des uploads:")
    print(os.listdir("/app/uploads"))
    sys.exit(1)

images = pdf_to_png_images_bytes(facture_path)
if not images:
    print("Erreur: PDF to Image a echoue (liste vide)")
    sys.exit(1)

client = genai.Client(api_key=api_key)
try:
    resp = client.models.generate_content(
        model=model,
        contents=[{"inline_data": {"mime_type": "image/png", "data": base64.b64encode(images[0]).decode("utf-8")}}, "Extrait JSON Facture"],
        config={"response_mime_type": "application/json"}
    )
    print("SUCCESS: Gemini a repondu")
    print(resp.text)
except Exception as e:
    print(f"ERROR: {str(e)}")
