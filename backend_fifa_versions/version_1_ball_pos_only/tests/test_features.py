import sys
import os
import matplotlib.pyplot as plt
import numpy as np

# Add src to python path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import load_chunk
from dsp_utils import apply_dsp_cleaning, create_windows, normalize_trajectory, compute_fourier_descriptors

# CONFIG
FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'Tracking Data', '3812.jsonl.bz2')
KICKOFF_TIME = 141.0
DURATION = 60 # 60 seconds

def test_feature_extraction():
    print("1. Loading Data...")
    df_raw = load_chunk(FILE_PATH, KICKOFF_TIME, DURATION)
    
    print("\n2. Applying DSP Cleaning...")
    df_clean = apply_dsp_cleaning(df_raw)
    
    print("\n3. Creating Windows (10s, 50% overlap)...")
    windows = create_windows(df_clean, window_size_sec=10, overlap_percent=0.5)
    print(f"   Created {len(windows)} windows.")
    
    if not windows:
        print("   ERROR: No windows created using current parameters.")
        return

    # Process just the first window for visual check
    win = windows[0]
    print(f"   First window size: {len(win)} frames.")
    
    print("\n4. Normalizing Trajectory...")
    win_norm = normalize_trajectory(win.copy())
    start_x = win_norm['x_norm'].iloc[0]
    start_y = win_norm['y_norm'].iloc[0]
    print(f"   Start Point (x,y): ({start_x:.2f}, {start_y:.2f}) - Should be (0.00, 0.00)")
    
    print("\n5. Computing Fourier Descriptors...")
    coeffs = compute_fourier_descriptors(win_norm, num_coeffs=5)
    print("   Top 5 Coefficients (X):")
    for i, c in enumerate(coeffs['x_coeffs']):
        print(f"     X[{i}]: {c.real:.2f} + {c.imag:.2f}j")
    
    # Optional Visualization
    print("\n6. Visualizing Normalization...")
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(win['x_smooth'], win['y_smooth'], label="Original Window")
    plt.title("Original Trajectory (World Coords)")
    plt.grid(True)
    plt.legend()
    plt.axis('equal')
    
    plt.subplot(1, 2, 2)
    plt.plot(win_norm['x_norm'], win_norm['y_norm'], color='orange', label="Normalized")
    plt.plot(0, 0, 'rx', markersize=10, label="Start (0,0)")
    plt.title("Normalized (Relative Motion)")
    plt.grid(True)
    plt.legend()
    plt.axis('equal')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    test_feature_extraction()
