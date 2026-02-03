import librosa
import numpy as np

class AudioProcessor:
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate

    def load_audio(self, file_path):
        """Loads audio and converts to mono."""
        try:
            signal, _ = librosa.load(file_path, sr=self.sample_rate, mono=True)
            return signal
        except Exception as e:
            raise ValueError(f"Error loading audio file: {e}")

    def extract_chroma_features(self, signal):
        """
        Extracts Cleaned Chroma features.
        Returns: (12, Time_Steps) numpy array
        """
        # 1. Harmonic-Percussive Source Separation
        # Isolate the melody (Harmonic) from the noise (Percussive)
        y_harmonic, _ = librosa.effects.hpss(signal)
        
        # 2. Extract Chroma using CQT (Constant-Q Transform)
        # CQT is much better for musical pitch detection than STFT
        chroma = librosa.feature.chroma_cqt(y=y_harmonic, sr=self.sample_rate)
        
        # 3. NORMALIZE the features (Critical Step)
        # This makes the features comparable even if one file is much louder
        return librosa.util.normalize(chroma)

    def compare_audio(self, user_signal, db_signal):
        """
        Compares signals using DTW with Cosine Similarity and Key Invariance.
        """
        # Extract features
        user_chroma = self.extract_chroma_features(user_signal)
        db_chroma = self.extract_chroma_features(db_signal)
        
        min_cost = float('inf')

        # --- KEY INVARIANCE (OPI) ---
        # Try all 12 musical keys to find the best match
        for shift in range(12):
            # Roll the chroma vector (Cyclic shift of notes)
            user_shifted = np.roll(user_chroma, shift, axis=0)
            
            # --- DYNAMIC TIME WARPING (DTW) ---
            # metric='cosine' is CRITICAL here. 
            # It measures the ANGLE between vectors, ignoring volume.
            # subseq=True allows the short humming to match a part of the long song.
            D, wp = librosa.sequence.dtw(X=user_shifted, Y=db_chroma, metric='cosine', subseq=True)
            
            # Calculate normalized cost of the path
            path_length = wp.shape[0]
            current_cost = D[-1, -1] / path_length
            
            if current_cost < min_cost:
                min_cost = current_cost

        # --- CONVERT COST TO SIMILARITY ---
        # Cosine distance ranges from 0.0 (Perfect) to 2.0 (Opposite).
        # A good hum match usually has a cost between 0.05 and 0.25.
        
        # Heuristic: 
        # If cost is 0.0 -> 100% match
        # If cost is 0.5 -> 0% match (too far to be considered similar)
        
        similarity = max(0, (1 - (min_cost * 2)) * 100)
        
        return round(float(similarity), 2)