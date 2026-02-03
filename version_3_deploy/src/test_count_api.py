import requests
import json
import os

url = "http://127.0.0.1:5000/api/v1/pass_sequences/count"
pkl_path = os.path.abspath("test_count_query.pkl")

payload = {
    "sequence_path": pkl_path
}

print(f"POST {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Request failed: {e}")
