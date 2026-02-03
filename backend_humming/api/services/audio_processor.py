import librosa
import numpy as np
from scipy import signal as scipy_signal

class AudioProcessor:
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate

    def load_audio(self, file_path):
        """Loads audio and converts to mono."""
        try:
            # Load with librosa (auto-converts to mono)
            sig, _ = librosa.load(file_path, sr=self.sample_rate, mono=True)
            return sig
        except Exception as e:
            raise ValueError(f"Error loading audio file: {e}")

    def preprocess_signal(self, sig):
        """
        Applies pre-processing to clean the signal for humming.
        1. Silence Trimming
        2. High-pass filter to remove rumble
        """
        # 1. Trim Silence (Top 60db)
        sig_trimmed, _ = librosa.effects.trim(sig, top_db=60)
        
        # If signal is too short after trim, return original or empty?
        if len(sig_trimmed) < self.sample_rate * 0.5: # Less than 0.5s
             # Fallback if aggressive trim removed everything (e.g. invalid quiet recording)
             # But if it's just silence, maybe we want to keep it trimmed or return original.
             # Let's keep trimmed if it has *some* data, else return original.
             if len(sig_trimmed) > 0:
                 pass
             else:
                 sig_trimmed = sig
        
        # 2. High-pass filter (Butterworth 2nd order, 100Hz cutoff)
        # Removes low freq noise (humming is usually > 100Hz)
        sos = scipy_signal.butter(N=2, Wn=100, btype='highpass', fs=self.sample_rate, output='sos')
        sig_filtered = scipy_signal.sosfilt(sos, sig_trimmed)
        
        return sig_filtered

    def extract_chroma_features(self, signal):
        """
        Extracts CHROMA CENS features.
        CENS (Chroma Energy Normalized Statistics) is robust to 
        tempo variations and articulation (perfect for humming).
        """
        # Pre-process first
        clean_signal = self.preprocess_signal(signal)
        
        # Extract CENS
        # hop_length=512 is standard. 
        # win_len_smooth: 41 (0.9s) = Smooth/Generic
        #                 11 (0.25s) = Intricate/Sharp (but sensitive to errors)
        #                 21 (0.5s) = Balanced
        chroma_cens = librosa.feature.chroma_cens(y=clean_signal, sr=self.sample_rate, hop_length=512, win_len_smooth=21)
        
        return chroma_cens

    def compare_audio(self, user_signal, db_signal):
        """
        Compares signals using DTW on Chroma CENS features.
        """
        # Extract features
        user_chroma = self.extract_chroma_features(user_signal)
        db_chroma = self.extract_chroma_features(db_signal)
        
        min_cost = float('inf')

        # --- KEY INVARIANCE ---
        # Try all 12 musical keys to find the best match
        for shift in range(12):
            # Roll the chroma vector for key invariance
            user_shifted = np.roll(user_chroma, shift, axis=0)
            
            # --- DTW ---
            # CENS features are already normalized and smoothed.
            # 'cosine' distance is still effective, or 'euclidean'.
            # Librosa docs suggest euclidean for CENS often, but cosine is good for orientation.
            # Let's stick with cosine for now as it handles amplitude differences well.
            D, wp = librosa.sequence.dtw(X=user_shifted, Y=db_chroma, metric='cosine', subseq=True)
            
            # Normalize cost
            path_length = wp.shape[0]
            current_cost = D[-1, -1] / path_length
            
            if current_cost < min_cost:
                min_cost = current_cost

        # --- CONVERT COST TO SIMILARITY ---
        # Relaxed Scoring for Real-World Usage
        # Previous settings (sigma=0.21, gamma=4) were too harsh ("The Wall").
        # We revert to a Standard Gaussian (gamma=2) with wider variance (sigma=0.3).
        # This provides a smooth decay curve.
        
        sigma = 0.30 
        gamma = 2    
        
        similarity = 100 * np.exp(- (min_cost / sigma) ** gamma)
        
        return round(float(similarity), 2)