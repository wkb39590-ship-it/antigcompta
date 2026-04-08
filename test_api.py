import os
from google import genai
import json

api_key = "AIzaSyAcpPqaZIznhuwfIZHl51UT0B_pnaHr10U"
client = genai.Client(api_key=api_key)

try:
    resp = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Say hello"
    )
    print(f"Status: OK")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Status: ERROR")
    print(f"Details: {str(e)}")
