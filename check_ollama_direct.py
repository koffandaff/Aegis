import requests
import json

def check():
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "IHA089/drana-infinity-3b:3b",
        "messages": [{"role": "user", "content": "hi"}],
        "stream": True
    }
    
    print(f"Connecting to {url}...")
    try:
        with requests.post(url, json=payload, stream=True) as r:
            print(f"Status: {r.status_code}")
            if r.status_code != 200:
                print(r.text)
                return
            
            for line in r.iter_lines():
                if line:
                    print(f"RAW: {line.decode('utf-8')}")
                    # Validate JSON
                    try:
                        data = json.loads(line)
                        if "message" in data:
                            print(f"Parsed Content: {data['message'].get('content')}")
                    except:
                        print("JSON Parse Error")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check()
