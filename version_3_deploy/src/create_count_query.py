import pickle
import os

test_pkl_path = os.path.abspath("test_count_query.pkl")

# Create a dummy query that mimics Match 10503, Length 6 (to get count 569)
# We don't need real vectors, just the metadata
query = {
    'game_id': '10503', 
    'event_id': 0, 
    'timestamp': 100.0, 
    'length': 6,
    'start_x': 0, 'start_y': 0,
    'vectors': [(0,0)]*6,
    'teammates': [], 'opponents': []
}

with open(test_pkl_path, 'wb') as qf:
    pickle.dump(query, qf)

print(f"Created test query for count at: {test_pkl_path}")
print("Contains Match 10503, Length 6")
