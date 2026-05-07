import sys
import os
from fastapi import status
from fastapi.testclient import TestClient

# Add current directory to path to import app
sys.path.append(os.getcwd())

from main import app

client = TestClient(app)

print("--- Testing Login with non-existent user 'fati' ---")
try:
    response = client.post("/auth/login", json={"username": "fati", "password": "password"})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    import traceback
    print("--- Exception ---")
    traceback.print_exc()
