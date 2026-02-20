import requests
import os

BASE = os.environ.get("BASE_URL", "http://localhost:8090")


def run():
    # NOTE: adjust credentials and ids as needed
    username = os.environ.get("TEST_AGENT_USERNAME", "wissal")
    password = os.environ.get("TEST_AGENT_PASSWORD", "secret")
    cabinet_id = int(os.environ.get("TEST_CABINET_ID", "4"))
    societe_id = int(os.environ.get("TEST_SOCIETE_ID", "3"))

    print(f"Config: username={username}, password={password}, cabinet_id={cabinet_id}, societe_id={societe_id}")
    print("Login...", username)
    r = requests.post(f"{BASE}/auth/login", json={"username": username, "password": password})
    print(f"  Status: {r.status_code}")
    if r.status_code != 200:
        print(f"  Response: {r.text[:500]}")
    r.raise_for_status()
    access = r.json().get("access_token")
    print("access_token obtained")

    print("Select societe...", societe_id)
    r = requests.post(f"{BASE}/auth/select-societe?token={access}", json={"cabinet_id": cabinet_id, "societe_id": societe_id})
    r.raise_for_status()
    session = r.json().get("session_token")
    print("session_token obtained")

    # Upload fixture
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample.pdf")
    print("Uploading", fixture_path)
    with open(fixture_path, "rb") as f:
        files = {"file": ("sample.pdf", f, "application/pdf")}
        r = requests.post(f"{BASE}/factures/upload", headers={"Authorization": f"Bearer {session}"}, files=files)
    r.raise_for_status()
    data = r.json()
    print("Upload response:", data)
    fid = data.get("id")

    # Download file
    print("Downloading preview for facture", fid)
    r = requests.get(f"{BASE}/factures/{fid}/file", headers={"Authorization": f"Bearer {session}"})
    if r.status_code != 200:
        raise SystemExit(f"Download failed: {r.status_code} {r.text}")
    out = os.path.join(os.getcwd(), f"facture_{fid}.pdf")
    with open(out, "wb") as fh:
        fh.write(r.content)
    print("Saved preview to", out)


if __name__ == "__main__":
    run()
