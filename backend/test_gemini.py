import google.generativeai as genai
import os

# Remplacez par votre clé API réelle
votre_cle = "AIzaSyBCkc9RrLbl9HRoOkZrR1LcYT RLkQw3yeI"

genai.configure(api_key=votre_cle)

# On utilise le modèle flash 1.5 que vous avez dans votre code
model = genai.GenerativeModel('gemini-2.5-flash')

try:
    print("Tentative de connexion à Gemini...")
    response = model.generate_content("Réponds par le mot 'Succès' si tu reçois ce message.")
    print(f"Résultat : {response.text}")
except Exception as e:
    print(f"Désolé, l'erreur persiste : \n{e}")