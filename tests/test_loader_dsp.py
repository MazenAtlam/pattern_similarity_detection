import bz2
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import os

# --- CONFIGURATION ---
FILE_PATH = r'data/Tracking Data/3812.jsonl.bz2'
KICKOFF_TIME = 141.0  # Start reading from 141 seconds
DURATION_TO_READ = 60 # Read 60 seconds
SAMPLING_RATE = 29.97 
CUTOFF_FREQ = 2.5     

def load_chunk_debug(filepath, start_time, duration):
    """
    Reads file and prints debug info about the JSON structure.
    Robustly handles missing 'ball' data.
    """
    if not os.path.exists(filepath):
        print(f"ERROR: File not found at {filepath}")
        return pd.DataFrame()

    data = []
    frames_to_read = int(duration * SAMPLING_RATE)
    frames_collected = 0
    
    print(f"DEBUG: Opening {filepath}...")
    
    with bz2.open(filepath, "rt", encoding="utf-8") as f:
        for i, line in enumerate(f):
            try:
                frame = json.loads(line)
                
                # DEBUG: Print keys of the first valid frame we find
                if i == 0:
                    print(f"DEBUG: First frame keys: {list(frame.keys())}")
                    if 'balls' in frame:
                         print(f"DEBUG: 'balls' content (first frame): {frame['balls']}")

                ts = frame.get('timestamp', 0)
                if not ts:
                    # In some datasets timestamp might be 'generatedTime' or similar if 'timestamp' is missing
                    # Based on keys seen: 'generatedTime', 'smoothedTime', 'videoTimeMs'
                    # Let's try generatedTime if timestamp is missing, or rely on frame indexes if needed
                    # But prompt implies 'timestamp' exists or we calculate it.
                    # The previous code used 'timestamp', let's stick to it or try 'periodElapsedTime' etc?
                    # The prompt says: "Skips to the Kickoff Time (141.0s) found in the event data"
                    # The keys show 'periodElapsedTime'.
                    # Let's check 'periodElapsedTime' or 'generatedTime'. 
                    # Actually, let's look at the keys again: 
                    # ['version', 'gameRefId', 'generatedTime', 'smoothedTime', ..., 'periodElapsedTime', ...]
                    # Standard statsbomb/similar usually has periodElapsedTime.
                    # I will try to use the existing 'timestamp' if present, else 'periodElapsedTime' or 'generatedTime'.
                    # For now I will keep 'timestamp' but add a fallback to 'periodElapsedTime' just in case.
                    ts = frame.get('timestamp') or frame.get('periodElapsedTime', 0)
                
                # 1. Skip if too early
                if ts < start_time:
                    continue
                
                # 2. Stop if we have enough data
                if frames_collected >= frames_to_read:
                    break
                
                # 3. Extract Ball Data (Handle missing ball)
                # Structure seems to be 'balls': [...]
                ball_list = frame.get('balls')
                bx, by = np.nan, np.nan
                
                if ball_list and isinstance(ball_list, list) and len(ball_list) > 0:
                    first_ball = ball_list[0]
                    # Check if 'x' and 'y' are in this ball object
                    if 'x' in first_ball and 'y' in first_ball:
                        bx = first_ball['x']
                        by = first_ball['y']
                # Fallback: maybe it IS 'ball' in some frames? 
                elif 'ball' in frame:
                     ball_obj = frame.get('ball')
                     if ball_obj and isinstance(ball_obj, dict):
                         bx = ball_obj.get('x', np.nan)
                         by = ball_obj.get('y', np.nan)
                
                data.append({'time': ts, 'x': bx, 'y': by})
                frames_collected += 1
                
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error on line {i}: {e}")

    print(f"DEBUG: Collected {len(data)} frames.")
    return pd.DataFrame(data)

def apply_dsp_cleaning(df):
    """
    Safely applies interpolation and filtering.
    """
    if df.empty:
        print("ERROR: DataFrame is empty. Check file path or KICKOFF_TIME.")
        return df

    # Check if we have ANY valid data
    valid_data_count = df['x'].notna().sum()
    print(f"DEBUG: Found {valid_data_count} frames with valid ball data out of {len(df)} total.")
    
    if valid_data_count < 10:
        print("WARNING: Not enough valid ball data to apply DSP filter. Returning raw data.")
        return df

    # 1. Linear Interpolation (fill gaps)
    df_clean = df.copy()
    # Interpolate only if we have at least some data points
    df_clean['x'] = df_clean['x'].interpolate(method='linear', limit_direction='both')
    df_clean['y'] = df_clean['y'].interpolate(method='linear', limit_direction='both')
    
    # Check if interpolation left any NaNs (e.g. if ALL were NaNs)
    if df_clean['x'].isna().all():
         print("WARNING: Data is all NaNs after interpolation. Skipping filter.")
         df_clean['x_smooth'] = df_clean['x']
         df_clean['y_smooth'] = df_clean['y']
         return df_clean

    # 2. Design Butterworth Filter
    nyq = 0.5 * SAMPLING_RATE
    normal_cutoff = CUTOFF_FREQ / nyq
    # Ensure cutoff is valid
    if normal_cutoff >= 1:
        print("WARNING: Cutoff frequency >= Nyquist. adjusting...")
        normal_cutoff = 0.99
        
    b, a = butter(N=2, Wn=normal_cutoff, btype='low', analog=False)
    
    # 3. Apply Filter
    try:
        # filtfilt requires valid non-NaN data.
        df_clean['x_smooth'] = filtfilt(b, a, df_clean['x'])
        df_clean['y_smooth'] = filtfilt(b, a, df_clean['y'])
    except Exception as e:
        print(f"DSP Filter Error: {e}")
        df_clean['x_smooth'] = df_clean['x']
        df_clean['y_smooth'] = df_clean['y']
        
    return df_clean

def visualize_results(df):
    if df.empty or 'x_smooth' not in df.columns:
        print("Cannot plot: No processed data available.")
        return

    plt.figure(figsize=(10, 8))
    
    # Plot spatial path
    # Filter out NaNs for plotting raw data to avoid warnings/blank plots if many NaNs
    valid_raw = df.dropna(subset=['x', 'y'])
    plt.plot(valid_raw['x'], valid_raw['y'], '.', label='Raw Input (Noisy)', color='red', alpha=0.3, markersize=3)
    
    plt.plot(df['x_smooth'], df['y_smooth'], '-', label='DSP Filtered (Clean)', color='blue', linewidth=2)
    
    plt.title(f"Ball Trajectory (First 60s of play)")
    plt.xlabel("X Position (meters)")
    plt.ylabel("Y Position (meters)")
    plt.legend()
    plt.grid(True)
    plt.axis('equal') # Important for pitch aspect ratio
    
    print("DEBUG: Showing plot...")
    plt.show()

if __name__ == "__main__":
    # 1. Load Data
    df_raw = load_chunk_debug(FILE_PATH, KICKOFF_TIME, DURATION_TO_READ)
    
    # 2. Clean
    df_processed = apply_dsp_cleaning(df_raw)
    
    # 3. Visualize
    visualize_results(df_processed)
