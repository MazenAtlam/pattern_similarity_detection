import pickle
import os

test_pkl_path = os.path.abspath("test_query.pkl")

# Create a LIST of dummy queries
queries = []

# Query 0: Horizontal
queries.append({
    'game_id': '000', 'event_id': 0, 'timestamp': 100.0, 'length': 1,
    'start_x': 0, 'start_y': 0,
    'vectors': [(10, 0)],
    'teammates': [], 'opponents': []
})

# Query 1: Vertical (We will target this one with index=1)
queries.append({
    'game_id': '000', 'event_id': 1, 'timestamp': 200.0, 'length': 1,
    'start_x': 50, 'start_y': 30,
    'vectors': [(0, 10)],
    'teammates': [], 'opponents': []
})

with open(test_pkl_path, 'wb') as qf:
    pickle.dump(queries, qf)

print(f"Created test query list at: {test_pkl_path}")
print("Contains 2 sequences.")
