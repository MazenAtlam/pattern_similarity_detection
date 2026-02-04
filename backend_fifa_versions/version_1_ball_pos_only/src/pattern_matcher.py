import numpy as np
import pandas as pd
from dsp_utils import create_windows, normalize_trajectory, compute_fourier_descriptors

class FingerprintDatabase:
    def __init__(self, window_size_sec=10, overlap_percent=0.5, num_coeffs=5):
        self.window_size_sec = window_size_sec
        self.overlap_percent = overlap_percent
        self.num_coeffs = num_coeffs
        self.database = [] # List of dicts: {window_id, start_time, coeffs}

    def build_from_dataframe(self, df_clean):
        """
        Ingests a cleaned dataframe, windows it, and builds the fingerprint database.
        """
        if df_clean.empty:
            print("WARNING: DataFrame is empty, cannot build database.")
            return

        windows = create_windows(df_clean, self.window_size_sec, self.overlap_percent)
        print(f"DEBUG: Processing {len(windows)} windows...")
        
        self.database = []
        
        for i, win in enumerate(windows):
            if win.empty: continue
            
            # Normalization
            win_norm = normalize_trajectory(win.copy())
            
            # Feature Extraction (Fingerprinting)
            coeffs_dict = compute_fourier_descriptors(win_norm, self.num_coeffs)
            
            # Store
            # We flatten coefficients for easier distance calculation later?
            # Or keep as complex numbers.
            # Let's keep structure:
            
            entry = {
                'window_id': i,
                'start_time': win['time'].iloc[0],
                'end_time': win['time'].iloc[-1],
                'x_coeffs': coeffs_dict['x_coeffs'],
                'y_coeffs': coeffs_dict['y_coeffs']
            }
            self.database.append(entry)
            
        print(f"DEBUG: Database built with {len(self.database)} fingerprint entries.")

    def find_nearest_neighbors(self, query_coeffs, top_k=5):
        """
        Finds the top_k closest matches to the query_coeffs (x, y) in the database.
        Uses Euclidean distance on the coefficient vectors.
        """
        if not self.database:
            return []
            
        results = []
        q_x = np.array(query_coeffs['x_coeffs'])
        q_y = np.array(query_coeffs['y_coeffs'])
        
        for entry in self.database:
            d_x = np.array(entry['x_coeffs'])
            d_y = np.array(entry['y_coeffs'])
            
            # Distance metric: Euclidean distance of complex coefficients
            # dist = sqrt( sum( |qx - dx|^2 ) + sum( |qy - dy|^2 ) )
            
            dist_x = np.linalg.norm(q_x - d_x)
            dist_y = np.linalg.norm(q_y - d_y)
            
            total_dist = dist_x + dist_y # Simple sum of distances
            
            results.append({
                'window_id': entry['window_id'],
                'start_time': entry['start_time'],
                'distance': total_dist
            })
            
        # Sort by distance (ascending)
        results.sort(key=lambda x: x['distance'])
        
        return results[:top_k]
