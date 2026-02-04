import numpy as np
import pickle
import os
from scipy.spatial.distance import cdist

class FingerprintDatabaseV3:
    def __init__(self, base_data_dir=None):
        if base_data_dir is None:
            self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_dir = os.path.join(self.base_dir, 'data', 'fifa')
        else:
            self.data_dir = base_data_dir
            
        self.current_length = 1
        self.database = []
        self.load_level(1)
        
    def load_level(self, length):
        """Loads the database for a specific number of passes (1-10)."""
        self.current_length = length
        db_path = os.path.join(self.data_dir, f'fingerprints_{length}pass.pkl')
        
        if os.path.exists(db_path):
            print(f"Loading L{length} database from {db_path}...")
            with open(db_path, 'rb') as f:
                self.database = pickle.load(f)
            print(f"Loaded {len(self.database)} sequences.")
        else:
            print(f"WARNING: Database not found at {db_path}")
            self.database = []

    def _vector_distance(self, vecs_a, vecs_b):
        """
        Computes mean Euclidean distance between sequence of vectors.
        vecs_a: list of (dx, dy)
        vecs_b: list of (dx, dy)
        Length is assumed same.
        """
        arr_a = np.array(vecs_a)
        arr_b = np.array(vecs_b)
        dist = np.linalg.norm(arr_a - arr_b, axis=1) # Per vector distance
        return np.mean(dist)

    def _chamfer_distance(self, set_a, set_b):
        """Standard Chamfer distance for player constellations."""
        if len(set_a) == 0 or len(set_b) == 0: return float('inf')
        dists = cdist(set_a, set_b, metric='euclidean')
        return np.mean(np.min(dists, axis=1)) + np.mean(np.min(dists, axis=0))

    def find_nearest_neighbors(self, query, top_k=5, w_vec=1.0, w_player=0.2):
        """
        Multi-component similarity:
        1. Vector Shape (Direction/Length) [High Importance]
        2. Player Configuration (Chamfer) [Lower Importance]
        """
        if not self.database: return []
        
        q_vecs = query['vectors']
        q_tm = np.array(query['teammates'])
        q_op = np.array(query['opponents'])
        
        results = []
        
        for entry in self.database:
            # Skip self
            if entry['game_id'] == query['game_id'] and entry['timestamp'] == query['timestamp']:
                continue
                
            # 1. Vector Distance (Primary)
            # Both query and entry are sequences of same length 'current_length'
            d_vec = self._vector_distance(q_vecs, entry['vectors'])
            
            # Optimization: If vector shape is too different, don't bother with expensive Chamfer?
            # Let's keep it simple for now.
            
            # 2. Player Distance (Secondary)
            # Comparing the snapshot at the START of the sequence
            e_tm = np.array(entry['teammates'])
            e_op = np.array(entry['opponents'])
            
            d_tm = self._chamfer_distance(q_tm, e_tm)
            d_op = self._chamfer_distance(q_op, e_op)
            
            total_dist = (w_vec * d_vec) + (w_player * (d_tm + d_op))
            
            results.append({
                'match': entry['game_id'],
                'event_id': entry['event_id'],
                'timestamp': entry['timestamp'],
                'length': entry['length'],
                'distance': total_dist,
                'data': entry
            })
            
        results.sort(key=lambda x: x['distance'])
        return results[:top_k]
