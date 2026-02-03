import numpy as np
import pickle
import os
from scipy.spatial.distance import cdist

class FingerprintDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            # Default to version 2 data path
            self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(self.base_dir, 'data', 'fingerprints_db.pkl')
        else:
            self.db_path = db_path
            
        self.database = []
        self.load_database()
        
    def load_database(self):
        if os.path.exists(self.db_path):
            print(f"Loading database from {self.db_path}...")
            with open(self.db_path, 'rb') as f:
                self.database = pickle.load(f)
            print(f"Loaded {len(self.database)} plays.")
        else:
            print(f"WARNING: Database not found at {self.db_path}")
            self.database = []

    def _chamfer_distance(self, set_a, set_b):
        """
        Computes Chamfer distance between two point sets (N, 2) and (M, 2).
        d(A, B) = mean(min_dist(a, B)) + mean(min_dist(b, A))
        """
        if len(set_a) == 0 or len(set_b) == 0:
            return float('inf')
            
        # Pairwise distances
        dists = cdist(set_a, set_b, metric='euclidean')
        
        # Min distance for each point in A to B
        min_a_to_b = np.min(dists, axis=1)
        
        # Min distance for each point in B to A
        min_b_to_a = np.min(dists, axis=0)
        
        return np.mean(min_a_to_b) + np.mean(min_b_to_a)

    def find_nearest_neighbors(self, query_play, top_k=5):
        """
        Finds similar plays to the query (a dictionary with 'teammates_rel' and 'opponents_rel').
        query_play should be one of the entries from the database (or similar structure).
        """
        if not self.database:
            return []
            
        q_teammates = np.array(query_play['teammates_rel'])
        q_opponents = np.array(query_play['opponents_rel'])
        
        results = []
        
        # Filter: Optionally filter by other attributes (e.g. similar field zone)
        # to speed up. For now, brute force all.
        
        for entry in self.database:
            # Skip self
            if entry['game_id'] == query_play['game_id'] and entry['event_id'] == query_play['event_id']:
                continue
                
            d_teammates = np.array(entry['teammates_rel'])
            d_opponents = np.array(entry['opponents_rel'])
            
            # Simple heuristic: Skip if player counts are vastly different?
            # Chamfer handles different sizes, but results might be weird if 10 vs 2.
            # Let's just compare.
            
            dist_team = self._chamfer_distance(q_teammates, d_teammates)
            dist_opp = self._chamfer_distance(q_opponents, d_opponents)
            
            total_dist = dist_team + dist_opp
            
            # Bonus: Penalize if ball position is very different?
            # The prompt asked for "positions of the players", but usually context matters.
            # We normalized ball to 0,0 relative, but maybe absolute zone matters?
            # Let's add a small penalty for absolute field position difference if they want "similar play in same area".
            # If they want "similar shape anywhere", we ignore absolute ball pos.
            # User said "checking the similar play... similar pass", usually implies shape.
            # Let's stick to shape (player relative positions).
            
            results.append({
                'match': entry['game_id'], # We might need to resolve this to Team names later
                'event_id': entry['event_id'],
                'timestamp': entry['timestamp'],
                'distance': total_dist,
                'data': entry # Return full data to visualize easily
            })
            
        results.sort(key=lambda x: x['distance'])
        return results[:top_k]
