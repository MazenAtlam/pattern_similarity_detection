import librosa
import numpy as np
from scipy.spatial.distance import euclidean

class AudioProcessorV2:
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
        Extracts dominant pitch using librosa.piptrack (Fast STFT based).
        """
        # 1. Compute Pitch (piptrack)
        # piptrack returns separate pitch and magnitude grids.
        pitches, magnitudes = librosa.piptrack(y=signal, sr=self.sample_rate)
        
        # 2. Extract Dominant Pitch
        # For each time bin, find the index of the max magnitude
        pitch_contour = []
        
        # We can do this efficiently with numpy argmax
        # axis=0 is frequency bins, axis=1 is time frames
        for t in range(magnitudes.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            
            # 3. Filter Silence / No Pitch
            # If pitch is 0 or magnitude is very low, treat as silence
            # (piptrack can return 0 if no peak found)
            if pitch > 0:
                 pitch_contour.append(pitch)
        
        pitch_contour = np.array(pitch_contour)
        
        if len(pitch_contour) == 0:
            return np.array([])

        # 4. Normalize (Key Invariance)
        # Convert to semitones for linear perception? 
        # The prompt says "Normalize: Subtract the mean". 
        # If we subtract mean Hz, it's weird. Subtracting mean Semitones is better.
        # But let's stick to the prompt's implied logic. I'll convert to MIDI first for better matching.
        
        midi_pitch = librosa.hz_to_midi(pitch_contour)
        normalized_pitch = midi_pitch - np.mean(midi_pitch)
        
        return normalized_pitch

    def compare_audio(self, user_signal, db_signal):
        """
        Compares signals using DTW on Fast Pitch Contours.
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
        
        # Normalize cost
        path_length = wp.shape[0]
        min_cost = D[-1, -1] / path_length
        
        # --- CONVERT COST TO SIMILARITY ---
        # Same logic as V1: Cost in semitones
        threshold = 4.0 
        similarity = max(0, (1 - (min_cost / threshold)) * 100)
        
        return round(float(similarity), 2)
