import sys
import os
import numpy as np

# Add src to python path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import load_chunk
from dsp_utils import apply_dsp_cleaning
from pattern_matcher import FingerprintDatabase

# CONFIG
FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'Tracking Data', '3812.jsonl.bz2')
KICKOFF_TIME = 141.0
DURATION = 120 # 2 minutes

def test_search_logic():
    print("1. Loading Data...")
    if not os.path.exists(FILE_PATH):
        print(f"ERROR: File not found: {FILE_PATH}")
        return

    df_raw = load_chunk(FILE_PATH, KICKOFF_TIME, DURATION)
    df_clean = apply_dsp_cleaning(df_raw)
    
    print("\n2. Building Database...")
    db = FingerprintDatabase()
    db.build_from_dataframe(df_clean)
    
    if not db.database:
        print("ERROR: Database is empty!")
        return
        
    print(f"   Database has {len(db.database)} entries.")
    
    # 3. Simulate Query
    query_idx = 10 
    if len(db.database) <= query_idx:
        print("Not enough windows for query.")
        return

    query_entry = db.database[query_idx]
    print(f"\n3. Querying Window {query_idx}...")
    
    # Run Search
    try:
        matches = db.find_nearest_neighbors(query_entry, top_k=6)
        print(f"   Matches returned: {len(matches)}")
        
        for m in matches:
             print(f"   - Match Win {m['window_id']} | Dist: {m['distance']:.4f}")
             
    except Exception as e:
        print(f"CRASH in find_nearest_neighbors: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search_logic()
