import requests
import os
import json

url = "http://127.0.0.1:5000/api/v1/pass_sequences/detect"
pkl_path = os.path.abspath("test_query.pkl")

# We ask for index 1 (the vertical one)
data = {
    "sequence_path": pkl_path,
    "number_of_passes": 1,
    "current_play_index": 1
}

print(f"Sending request to {url}")
print(f"Payload: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print("Response not JSON:", response.text)
except Exception as e:
    print(f"Request failed: {e}")
