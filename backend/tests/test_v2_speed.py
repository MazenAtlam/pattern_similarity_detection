import sys
import os
import time
import numpy as np
import librosa

# Adjust path to find src/backend
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)

from api.services.audio_processor import AudioProcessor
from api.services.audio_processor_v1 import AudioProcessorV1
from api.services.audio_processor_v2 import AudioProcessorV2

def generate_tone(freq, duration, sr=22050):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * freq * t)

def test_speed():
    print("--- Speed Test: V0 vs V1 vs V2 ---")
    
    # Generate 5 second audio
    sr = 22050
    audio = np.concatenate([generate_tone(f, 1.0, sr) for f in [261, 329, 392, 523, 659]])
    
    # Initialize
    v0 = AudioProcessor()
    v1 = AudioProcessorV1()
    v2 = AudioProcessorV2()
    
    # Test V0 (Chroma CENS)
    start = time.time()
    for _ in range(5):
        feat = v0.extract_chroma_features(audio)
    end = time.time()
    print(f"V0 (CENS) Avg Time: {(end-start)/5:.4f}s")
    
    # Test V1 (PyIn)
    start = time.time()
    for _ in range(5):
        try:
            feat = v1.extract_pitch_features(audio)
        except:
            pass
    end = time.time()
    print(f"V1 (PyIn) Avg Time: {(end-start)/5:.4f}s")
    
    # Test V2 (PipTrack)
    start = time.time()
    for _ in range(5):
        feat = v2.extract_pitch_contour(audio)
    end = time.time()
    print(f"V2 (PipTrack) Avg Time: {(end-start)/5:.4f}s")
    
    # Test Comparison (Self-match)
    print("\n--- Accuracy/Sanity Check (Self-Match) ---")
    score_v0 = v0.compare_audio(audio, audio)
    score_v1 = v1.compare_audio(audio, audio)
    score_v2 = v2.compare_audio(audio, audio)
    
    print(f"V0 Self-Score: {score_v0}%")
    print(f"V1 Self-Score: {score_v1}%")
    print(f"V2 Self-Score: {score_v2}%")

if __name__ == "__main__":
    test_speed()
