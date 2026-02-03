import requests
import os
import json

url = "http://127.0.0.1:5000/api/v1/pass_sequences/detect"
pkl_path = os.path.abspath("test_query.pkl")

data = {"sequence_path": pkl_path}

print(f"Sending request to {url} with {pkl_path}")
try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print("Response not JSON:", response.text)
except Exception as e:
    print(f"Request failed: {e}")
