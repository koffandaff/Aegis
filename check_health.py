import requests
import json

try:
    response = requests.get("http://localhost:8000/api/chat/health")
    print("Status:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", e)
