from google import genai
from google.genai.errors import APIError

def test_key():
    api_key = "AIzaSyBqbTZgYSEKGXEITaDU40Jm2mCq1FrBtVU"
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents='Test API'
        )
        print("SUCCES:", response.text)
    except APIError as e:
        print(f"Erreur API: {e}")
    except Exception as e:
        print(f"Autre erreur: {e}")

if __name__ == "__main__":
    test_key()
