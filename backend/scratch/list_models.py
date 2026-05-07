import os
from google import genai
from google.genai.errors import APIError

def test_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Pas de clé API trouvée.")
        return

    try:
        client = genai.Client(api_key=api_key)
        models = client.models.list()
        print("Modèles disponibles :")
        for m in models:
            if "generateContent" in m.supported_actions and "vision" not in m.name.lower():
                print(f"- {m.name} (Version: {m.version})")
    except APIError as e:
        print(f"Erreur API: {e}")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_models()
