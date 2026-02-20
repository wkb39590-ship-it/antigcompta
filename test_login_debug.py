import requests
import json

print("Testing login...")
r = requests.post('http://127.0.0.1:8090/auth/login', json={"username":"wissal","password":"password123"})
print("Status:", r.status_code)
print("Headers:", dict(r.headers))
print("Text:", r.text[:500])
if r.status_code == 200:
    print("Success:", json.dumps(r.json(), indent=2)[:500])
else:
    print("Failed response body:", r.text)
