import requests
import json
import time
import uuid

BASE_URL = "http://localhost:8000"

def debug_stream():
    # 0. Check Health
    print("Checking Health...")
    try:
        h = requests.get(f"{BASE_URL}/api/chat/health")
        print(f"Health: {h.status_code}")
        print(json.dumps(h.json(), indent=2))
        
        if not h.json().get("ollama_connected"):
            print("WARNING: OLLAMA NOT CONNECTED")
    except Exception as e:
        print(f"Health check failed: {e}")

    # 1. Login
    print("\nAuthenticating...")
    
    creds = [
        ("admin@fsociety.com", "Admin123!"),
        ("mrrobot@fsociety.com", "Elliot123!"),
        ("alice@example.com", "Demo123!"),
    ]
    
    token = None
    
    for email, password in creds:
        print(f"Trying {email}...")
        login = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password})
        if login.status_code == 200:
            print("Login success!")
            token = login.json()["access_token"]
            break
        else:
            print(f"Failed: {login.status_code}")
    
    if not token:
        print("All hardcoded creds failed. Trying signup...")
        unique_id = str(uuid.uuid4())[:8]
        email = f"debug_{unique_id}@example.com"
        password = "password123"
        print(f"Creating user: {email}")
        
        signup = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "username": f"debugger_{unique_id}",
            "email": email,
            "password": password,
            "full_name": "Debug User"
        })
        
        if signup.status_code == 201:
            print("Signup success")
            login = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password})
            if login.status_code == 200:
                token = login.json()["access_token"]
            else:
                print(f"Login after signup failed: {login.text}")
                return
        else:
            print(f"Signup failed: {signup.text}")
            return

    if not token:
        print("Could not authenticate.")
        return
        
    print(f"Got token: {token[:10]}...")
    print(f"Got token: {token[:10]}...")

    # 2. Start Chat
    print("\nStarting Chat Stream...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # First create a session implicitly by sending a message
    payload = {
        "message": "Hello, are you there?",
        "session_id": None
    }
    
    with requests.post(f"{BASE_URL}/api/chat/send", json=payload, headers=headers, stream=True) as r:
        print(f"Response Status: {r.status_code}")
        print("--- STREAM START ---")
        for line in r.iter_lines():
            if line:
                print(f"RECEIVED: {line.decode('utf-8')}")
            else:
                # Keep alive packet or empty line
                pass
        print("--- STREAM END ---")

if __name__ == "__main__":
    debug_stream()
