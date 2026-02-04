import librosa
import numpy as np
from scipy.signal import medfilt
from scipy.spatial.distance import euclidean

class AudioProcessorV3:
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate

    def load_audio(self, file_path):
        """Loads audio and converts to mono."""
        try:
            sig, _ = librosa.load(file_path, sr=self.sample_rate, mono=True)
            return sig
        except Exception as e:
            raise ValueError(f"Error loading audio file: {e}")

    def extract_pitch_contour(self, signal):
        """
        Extracts dominant pitch with refined accuracy steps:
        1. HPSS (Vocal Isolation)
        2. pip_track constrained to Vocal Range (80-1000Hz)
        3. Global Thresholding
        4. Silence Trimming
        5. Z-Score Normalization
        """
        # 1. Vocal Isolation (HPSS)
        # Separate harmonic (vocals) from percussive (drums)
        y_harmonic, _ = librosa.effects.hpss(signal)
        
        # 2. Fast Tracking with Human Vocal Range Constraints
        # fmin=80Hz (~Low E2), fmax=1000Hz (~High C6) covers reasonable humming range
        pitches, magnitudes = librosa.piptrack(
            y=y_harmonic, 
            sr=self.sample_rate,
            fmin=80,
            fmax=1000
        )
        
        # 3. Smart Thresholding (Global)
        pitch_contour = []
        global_max_mag = np.max(magnitudes)
        mag_threshold = global_max_mag * 0.10  # Must be > 10% of max loudness to count
        
        for t in range(magnitudes.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            mag = magnitudes[index, t]
            
            if pitch > 0 and mag > mag_threshold:
                 pitch_contour.append(pitch)
            else:
                 # Pad with 0 for silence (will trim later)
                 pitch_contour.append(0)
        
        pitch_contour = np.array(pitch_contour)
        
        # 4. Smoothing
        if len(pitch_contour) > 5:
            pitch_contour = medfilt(pitch_contour, kernel_size=5)

        # 5. Silence Trimming
        # Strip leading/trailing zeros (silence)
        # distinct from the 0s inside the hum
        pitch_contour = np.trim_zeros(pitch_contour)
        
        if len(pitch_contour) < 10:
            return np.array([])
            
        # Remove internal zeros (optional, but handling silence in DTW is tricky)
        # For now, let's filter purely positive pitches for the contour shape
        # This effectively concatenates the sung parts.
        pitch_contour = pitch_contour[pitch_contour > 0]
        
        if len(pitch_contour) < 10:
             return np.array([])

        # 6. Z-Score Normalization (Shape Matching)
        # (x - mean) / std
        # Matches "flat" hum to "expressive" song better than simple mean subtraction
        std_val = np.std(pitch_contour)
        if std_val == 0:
            std_val = 1.0 # Avoid div by zero for flat lines
            
        normalized_pitch = (pitch_contour - np.mean(pitch_contour)) / std_val
        
        return normalized_pitch

    def compare_audio(self, user_signal, db_signal):
        """
        Compares signals using DTW on Refined Pitch Contours.
        Includes penalty for extreme length variation.
        """
        # Extract features
        user_pitch = self.extract_pitch_contour(user_signal)
        db_pitch = self.extract_pitch_contour(db_signal)
        
        # Handle cases where no pitch was found
        if len(user_pitch) < 10 or len(db_pitch) < 10:
            return 0.0
            
        # --- DTW ---
        user_pitch_2d = user_pitch.reshape(1, -1)
        db_pitch_2d = db_pitch.reshape(1, -1)
        
        # Subsequence DTW
        D, wp = librosa.sequence.dtw(X=user_pitch_2d, Y=db_pitch_2d, metric='euclidean', subseq=True)
        
        # Raw Match Cost
        path_length = wp.shape[0]
        match_cost = D[-1, -1] / path_length
        
        # --- PENALTY LOGIC ---
        # Did we match a tiny fragment?
        # User hum length (N) vs Matched Subsequence Length (M)
        # wp[:, 0] are indices in User (X)
        # wp[:, 1] are indices in DB (Y)
        
        # In subsequence DTW, the user query (X) is usually fully consumed (or mostly).
        # The subsequence in Y is from min(wp_y) to max(wp_y).
        
        # Length of hum
        hum_len = len(user_pitch)
        
        # Length of matched segment in song
        y_indices = wp[:, 1]
        matched_segment_len = np.max(y_indices) - np.min(y_indices)
        
        # Ratio: How stretched/compressed is the match?
        # Ideal ratio is 1.0 (Hum duration == Match duration)
        # If hum is 5s and match is 0.5s, ratio is 0.1 -> Bad
        
        ratio = 0.0
        if hum_len > 0:
            ratio = matched_segment_len / hum_len
        
        # Penalize if ratio is too far from 1.0 (e.g. < 0.5 or > 2.0)
        length_penalty = 0.0
        if ratio < 0.5 or ratio > 2.0:
            length_penalty = 0.5 # Add flat cost penalty
            
        final_cost = match_cost + length_penalty
        
        # --- CONVERT COST TO SIMILARITY ---
        # Z-Normalized distances are roughly in reasonable range (0.0 to 2.0 usually)
        # Threshold needs to be tighter for Z-score than raw semitones
        # 0.5 avg distance in Z-space is decent correlation.
        
        threshold = 2.0 
        
        similarity = max(0, (1 - (final_cost / threshold)) * 100)
        
        return round(float(similarity), 2)
