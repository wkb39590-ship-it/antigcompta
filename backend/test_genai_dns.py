import os
from google import genai
import socket

print(f"Testing DNS: {socket.gethostbyname('generativelanguage.googleapis.com')}")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
try:
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents='hello'
    )
    print("Success! Gemini response:", response.text)
except Exception as e:
    print(f"Error calling Gemini: {e}")
