import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

def apply_dsp_cleaning(df, sampling_rate=29.97, cutoff_freq=2.5):
    """
    Applies linear interpolation and Butterworth low-pass filtering.
    """
    if df.empty:
        return df

    # Check validity
    valid_data_count = df['x'].notna().sum()
    if valid_data_count < 10:
        return df

    # 1. Interpolation
    df_clean = df.copy()
    df_clean['x'] = df_clean['x'].interpolate(method='linear', limit_direction='both')
    df_clean['y'] = df_clean['y'].interpolate(method='linear', limit_direction='both')
    
    if df_clean['x'].isna().all():
        df_clean['x_smooth'] = df_clean['x']
        df_clean['y_smooth'] = df_clean['y']
        return df_clean

    # 2. Butterworth Filter
    nyq = 0.5 * sampling_rate
    normal_cutoff = cutoff_freq / nyq
    if normal_cutoff >= 1: normal_cutoff = 0.99
    
    b, a = butter(N=2, Wn=normal_cutoff, btype='low', analog=False)
    
    try:
        df_clean['x_smooth'] = filtfilt(b, a, df_clean['x'])
        df_clean['y_smooth'] = filtfilt(b, a, df_clean['y'])
    except:
        df_clean['x_smooth'] = df_clean['x']
        df_clean['y_smooth'] = df_clean['y']
        
    return df_clean

def create_windows(df, window_size_sec, overlap_percent, sampling_rate=29.97):
    """
    Slices the dataframe into sliding windows.
    Returns a list of DataFrames.
    """
    if df.empty:
        return []

    window_frames = int(window_size_sec * sampling_rate)
    step_frames = int(window_frames * (1 - overlap_percent))
    
    windows = []
    total_frames = len(df)
    
    for start_idx in range(0, total_frames - window_frames + 1, step_frames):
        end_idx = start_idx + window_frames
        chunk = df.iloc[start_idx:end_idx].copy()
        
        # Only accept windows that are mostly valid (optional check)
        # For now, we take them all as we interpolated already
        windows.append(chunk)
        
    return windows

def normalize_trajectory(df_window, x_col='x_smooth', y_col='y_smooth'):
    """
    Shifts coordinates so the play starts at (0,0).
    Adds 'x_norm' and 'y_norm' columns.
    """
    if df_window.empty:
        return df_window
        
    # Get starting position
    start_x = df_window[x_col].iloc[0]
    start_y = df_window[y_col].iloc[0]
    
    df_window['x_norm'] = df_window[x_col] - start_x
    df_window['y_norm'] = df_window[y_col] - start_y
    
    return df_window

def compute_fourier_descriptors(df_window, num_coeffs=5, x_col='x_norm', y_col='y_norm'):
    """
    Computes FFT of the trajectory and returns the first `num_coeffs` coefficients.
    We treat the 2D signal as a complex signal z = x + iy? 
    OR we compute FFT for X and Y separately as per prompt "fft(x_signal) and fft(y_signal)".
    
    Returns:
        dict: {'x_coeffs': [...], 'y_coeffs': [...]}
        Coefficients are stored as complex numbers (or tuples of real/imag if needed for JSON).
    """
    if df_window.empty:
        return {'x_coeffs': [], 'y_coeffs': []}
        
    # Extract signals
    x_signal = df_window[x_col].values
    y_signal = df_window[y_col].values
    
    # Compute FFT
    fft_x = np.fft.fft(x_signal)
    fft_y = np.fft.fft(y_signal)
    
    # Normalize by length (optional, but good for scale invariance if window sizes varied)
    # However, standard FFT is fine if window size is fixed.
    
    # Keep low frequences (first num_coeffs)
    # Note: fft_x[0] is the DC component (mean position). 
    # Since we normalized to start at 0,0, the mean might not be 0, but it tells us the "center of gravity" relative to start.
    
    return {
        'x_coeffs': fft_x[:num_coeffs],
        'y_coeffs': fft_y[:num_coeffs]
    }
