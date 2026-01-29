import bz2
import json
import numpy as np
import pandas as pd
import os

# Configuration defaults
DEFAULT_SAMPLING_RATE = 29.97

def load_chunk(filepath, start_time, duration, sampling_rate=DEFAULT_SAMPLING_RATE):
    """
    Reads a chunk of the tracking data from a .bz2 JSONL file.
    
    Args:
        filepath (str): Path to the .jsonl.bz2 file.
        start_time (float): Timestamp to start reading from.
        duration (float): Duration in seconds to read.
        sampling_rate (float): Expected sampling rate (hz) to calculate frame count.
        
    Returns:
        pd.DataFrame: DataFrame with 'time', 'x', 'y' columns.
    """
    if not os.path.exists(filepath):
        print(f"ERROR: File not found at {filepath}")
        return pd.DataFrame()

    data = []
    frames_to_read = int(duration * sampling_rate)
    frames_collected = 0
    
    print(f"DEBUG: Opening {filepath}...")
    
    with bz2.open(filepath, "rt", encoding="utf-8") as f:
        for i, line in enumerate(f):
            try:
                frame = json.loads(line)
                
                # Timestamp handling
                ts = frame.get('timestamp') or frame.get('periodElapsedTime', 0)
                
                # 1. Skip if too early
                if ts < start_time:
                    continue
                
                # 2. Stop if we have enough data
                if frames_collected >= frames_to_read:
                    break
                
                # 3. Extract Ball Data (Handle missing ball)
                # Structure: 'balls': [{'x':..., 'y':...}, ...]
                ball_list = frame.get('balls')
                bx, by = np.nan, np.nan
                
                if ball_list and isinstance(ball_list, list) and len(ball_list) > 0:
                    first_ball = ball_list[0]
                    if 'x' in first_ball and 'y' in first_ball:
                        bx = first_ball['x']
                        by = first_ball['y']
                elif 'ball' in frame:
                     # Fallback for old format
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
