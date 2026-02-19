#!/usr/bin/env python3
"""Test multi-société isolation with session tokens"""

import requests
import json
from base64 import b64decode

BASE_URL = "http://localhost:8090"

def test_session_isolation():
    """Test that users can only access their own société's data"""
    
    print("=" * 60)
    print("Testing Multi-Société Isolation with Session Tokens")
    print("=" * 60)
    
    # Step 1: Login as agent1
    print("\n[1] Logging in as agent1...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "agent1", "password": "password123"}
    )
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    access_token = login_response.json()["access_token"]
    print(f"✅ Got access_token: {access_token[:20]}...")
    
    # Step 2: Select société 1
    print(f"\n[2] Selecting société 1...")
    select_response = requests.post(
        f"{BASE_URL}/auth/select-societe",
        params={"token": access_token}
    )
    if select_response.status_code != 200:
        print(f"❌ Select failed: {select_response.text}")
        return
    
    session_token_1 = select_response.json()["session_token"]
    print(f"✅ Got session_token for société 1: {session_token_1[:20]}...")
    
    # Decode and print session payload
    try:
        parts = session_token_1.split('.')
        payload = json.loads(b64decode(parts[1] + '=='))  # Add padding
        print(f"   Session payload: societe_id={payload.get('societe_id')}, raison_sociale={payload.get('societe_raison_sociale')}")
    except:
        pass
    
    # Step 3: List factures for société 1 using session token
    print(f"\n[3] Listing factures for société 1 (with session token)...")
    headers_1 = {"Authorization": f"Bearer {session_token_1}"}
    list_response_1 = requests.get(
        f"{BASE_URL}/factures/",
        headers=headers_1
    )
    if list_response_1.status_code != 200:
        print(f"❌ List failed: {list_response_1.text}")
        return
    
    factures_1 = list_response_1.json()
    print(f"✅ Got {len(factures_1)} factures for société 1")
    
    # Step 4: Select société 2
    print(f"\n[4] Selecting société 2...")
    select_response_2 = requests.post(
        f"{BASE_URL}/auth/select-societe",
        params={"token": access_token}
    )
    if select_response_2.status_code != 200:
        print(f"❌ Select failed: {select_response_2.text}")
        return
    
    session_token_2 = select_response_2.json()["session_token"]
    print(f"✅ Got session_token for société 2: {session_token_2[:20]}...")
    
    try:
        parts = session_token_2.split('.')
        payload = json.loads(b64decode(parts[1] + '=='))
        print(f"   Session payload: societe_id={payload.get('societe_id')}, raison_sociale={payload.get('societe_raison_sociale')}")
    except:
        pass
    
    # Step 5: List factures for société 2
    print(f"\n[5] Listing factures for société 2 (with different session token)...")
    headers_2 = {"Authorization": f"Bearer {session_token_2}"}
    list_response_2 = requests.get(
        f"{BASE_URL}/factures/",
        headers=headers_2
    )
    if list_response_2.status_code != 200:
        print(f"❌ List failed: {list_response_2.text}")
        return
    
    factures_2 = list_response_2.json()
    print(f"✅ Got {len(factures_2)} factures for société 2")
    
    # Step 6: Test cross-société access prevention
    if len(factures_1) > 0:
        facture_1_id = factures_1[0]["id"]
        print(f"\n[6] Attempting to access facture #{facture_1_id} (from société 1) with société 2 session...")
        response = requests.get(
            f"{BASE_URL}/factures/{facture_1_id}",
            headers=headers_2
        )
        
        if response.status_code == 403:
            print(f"✅ CORRECTLY DENIED: {response.json()}")
        elif response.status_code == 404:
            print(f"✅ CORRECTLY NOT FOUND: {response.json()}")
        else:
            print(f"❌ SECURITY ISSUE: Got {response.status_code} instead of 403/404: {response.json()}")
    
    # Step 7: Test request without session token
    print(f"\n[7] Attempting to list factures without Authorization header...")
    response = requests.get(f"{BASE_URL}/factures/")
    
    if response.status_code == 401:
        print(f"✅ CORRECTLY DENIED: {response.json()}")
    else:
        print(f"❌ SECURITY ISSUE: Got {response.status_code} instead of 401: {response.text}")
    
    print("\n" + "=" * 60)
    print("Multi-Société Isolation Tests Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_session_isolation()
