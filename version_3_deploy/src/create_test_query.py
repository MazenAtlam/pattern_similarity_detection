import requests
import pickle
import os
import json

# 1. Create a dummy test pickle file (simulating a query)
# We need a valid structure: {'vectors': [...], 'teammates': [], ...}
test_pkl_path = os.path.abspath("test_query.pkl")

# Let's verify we have data first
# Link to V3 data
DATA_V3 = os.path.abspath("version_3_more_than_one_pass/data/fingerprints_1pass.pkl")

if os.path.exists(DATA_V3):
    with open(DATA_V3, 'rb') as f:
        data = pickle.load(f)
        if data:
            # Pick the first one as query
            query = data[0]
            with open(test_pkl_path, 'wb') as qf:
                pickle.dump(query, qf)
            print(f"Created test query from real data: {test_pkl_path}")
else:
    print("V3 Data not found, creating synthetic query.")
    query = {
        'game_id': '000', 'event_id': 0, 'timestamp': 120.5, 'length': 1,
        'start_x': 0, 'start_y': 0,
        'vectors': [(10, 5)],
        'teammates': [], 'opponents': []
    }
    with open(test_pkl_path, 'wb') as qf:
        pickle.dump(query, qf)

# 2. Start Server (Background) - In this script we assume server is running?
# Actually agent can't easily start server and run script in parallel easily in one block without spawn.
# But I can try to run this script IF the server was started in background.
# I will output the curl command for the agent to run explicitly.

print("To test, run the Flask app in one terminal, and then run:")
print(f'curl -X POST -H "Content-Type: application/json" -d \'{{"sequence_path": "{test_pkl_path.replace(chr(92), chr(47))}"}}\' http://127.0.0.1:5000/api/v1/pass_sequences/detect')
