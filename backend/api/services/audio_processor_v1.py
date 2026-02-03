import librosa
import numpy as np
from scipy.spatial.distance import euclidean

class AudioProcessorV1:
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate

    def load_audio(self, file_path):
        """Loads audio and converts to mono."""
        try:
            sig, _ = librosa.load(file_path, sr=self.sample_rate, mono=True)
            return sig
        except Exception as e:
            raise ValueError(f"Error loading audio file: {e}")

    def extract_pitch_features(self, signal):
        """
        Extracts Pitch Contour (F0) using librosa.pyin.
        Normalizes by subtracting the mean (Key Invariance).
        """
        # 1. Harmonic-Percussive Separartion (optional, but helps with polyphonic songs)
        # We might skip this for V1 simple implementation as requested, 
        # but the prompt mentioned just "Use librosa.pyin".
        # Let's stick to the prompt's steps: pyin -> filter -> normalize.
        
        # Estimate pitch (F0)
        # fmin=65Hz (C2), fmax=2093Hz (C7) covers most vocal ranges
        f0, voiced_flag, voiced_probs = librosa.pyin(
            signal, 
            fmin=librosa.note_to_hz('C2'), 
            fmax=librosa.note_to_hz('C7'), 
            sr=self.sample_rate
        )
        
        # f0 contains NaNs for unvoiced frames. 
        # We need a continuous curve for DTW, or handle NaNs.
        # Strategy: Filter out unvoiced parts (keep only the melody).
        
        valid_f0 = f0[~np.isnan(f0)]
        
        if len(valid_f0) == 0:
            return np.array([]) # Return empty if no pitch detected

        # Convert to Semitones (Linear pitch space instead of exponential Hz)
        # This makes comparison perception-based.
        midi_pitch = librosa.hz_to_midi(valid_f0)
        
        # Zero-Mean Normalization (Key Invariance)
        # Allows matching a melody regardless of absolute pitch (singing higher/lower).
        normalized_pitch = midi_pitch - np.mean(midi_pitch)
        
        return normalized_pitch

    def compare_audio(self, user_signal, db_signal):
        """
        Compares signals using DTW on Pitch Contours.
        """
        # Extract features
        user_pitch = self.extract_pitch_features(user_signal)
        db_pitch = self.extract_pitch_features(db_signal)
        
        # Handle cases where no pitch was found
        if len(user_pitch) < 10 or len(db_pitch) < 10:
            return 0.0
            
        # --- DTW ---
        # Compare 1D arrays using Euclidean distance
        # We need to reshape for librosa.sequence.dtw if using it, 
        # but librosa dtw takes (d, n) and (d, m). 
        # Here we have 1D arrays (n,) and (m,). Reshape to (1, n).
        
        user_pitch_2d = user_pitch.reshape(1, -1)
        db_pitch_2d = db_pitch.reshape(1, -1)
        
        # Subsequence DTW allows the hum to match a part of the song
        D, wp = librosa.sequence.dtw(X=user_pitch_2d, Y=db_pitch_2d, metric='euclidean', subseq=True)
        
        # Normalize cost
        path_length = wp.shape[0]
        min_cost = D[-1, -1] / path_length
        
        # --- CONVERT COST TO SIMILARITY ---
        # Cost is in semitones (average error).
        # 0.5 semitones off is amazing.
        # 2.0 semitones off is okay.
        # > 5.0 is bad.
        
        # Let's define a similarity heuristic
        # If cost = 0, similarity = 100
        # If cost = 3 (semitones), similarity = 0
        
        threshold = 4.0 # Tolerance in semitones
        similarity = max(0, (1 - (min_cost / threshold)) * 100)
        
        return round(float(similarity), 2)
