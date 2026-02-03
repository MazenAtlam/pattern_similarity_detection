import sys
import os
import numpy as np
from scipy import signal as scipy_signal

# Adjust path to find src/backend
# Test file is in backend/tests/
# Audio processor is in backend/api/services/
# We need to add 'backend' to sys.path so we can import 'api'
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)

from api.services.audio_processor import AudioProcessor

def generate_tone(freq, duration, sr=22050):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * freq * t)

def test_humming_logic():
    print("--- Testing Audio Logic (Synthetic) ---")
    ap = AudioProcessor()
    
    # 1. Create a "Song" (Melody: C4, E4, G4, C5)
    # Simple sine waves
    sr = 22050
    note_duration = 0.5
    song = np.concatenate([
        generate_tone(261.63, note_duration, sr), # C4
        generate_tone(329.63, note_duration, sr), # E4
        generate_tone(392.00, note_duration, sr), # G4
        generate_tone(523.25, note_duration, sr), # C5
    ])
    
    # 2. Create a "Hum" (Same melody, but slightly different)
    # Add some noise and slight pitch shift (to test CENS robustness)
    # Note: CENS is robust to micro-pitch shifts, but key-invariance handles transposition.
    # Let's just add noise for now and maybe slightly different duration
    
    hum_part1 = generate_tone(261.63, 0.6, sr) # Longer first note
    hum_part2 = generate_tone(329.63, 0.4, sr) # Shorter
    hum_part3 = generate_tone(392.00, 0.5, sr)
    hum_part4 = generate_tone(523.25, 0.5, sr)
    
    # Add silence at start/end
    silence = np.zeros(int(sr * 1.0))
    
    hum_clean = np.concatenate([hum_part1, hum_part2, hum_part3, hum_part4])
    noise = np.random.normal(0, 0.02, hum_clean.shape) 
    
    # Mix: Silence + Hum + Noise + Silence
    hum_noisy = np.concatenate([silence, hum_clean + noise, silence])
    
    print(f"Song Duration: {len(song)/sr:.2f}s")
    print(f"Hum Duration (w/ silence): {len(hum_noisy)/sr:.2f}s")
    
    # 3. Compare (Match Expected)
    print("\nComparing Song vs. Noisy/Padded Hum...")
    # Add simple time-stretch simulation (resample)
    # Simulate hum being 20% slower
    hum_slower = scipy_signal.resample(hum_noisy, int(len(hum_noisy) * 1.2))
    
    # We need to access the raw cost, but compare_audio returns the final score.
    # Let's temporarily just use the score to infer the cost, or we can assume the cost.
    # Actually, let's just observe the score with the CURRENT formula.
    
    score_match = ap.compare_audio(hum_noisy, song)
    print(f"Direct Match Score: {score_match}%")
    
    score_slower = ap.compare_audio(hum_slower, song)
    print(f"Slower (20%) Match Score: {score_slower}%")
    
    if score_slower < 60:
        print("⚠️  OBSERVATION: Score dropped significantly due to tempo change.")
    
    # 3b. Fast Melody Check (Intricate details)
    # Fast notes: C, D, E, F, G, A, B, C (all 0.1s)
    fast_song = np.concatenate([generate_tone(f, 0.1, sr) for f in [261, 293, 329, 349, 392, 440, 493, 523]])
    fast_hum = fast_song + np.random.normal(0, 0.01, fast_song.shape) # Minimal noise
    
    print("\nComparing Fast Intricate Melody...")
    score_fast = ap.compare_audio(fast_hum, fast_song)
    print(f"Fast Melody Score: {score_fast}% (Target > 80%)")
    
    print(f"Fast Melody Score: {score_fast}% (Target > 80%)")

    # 3c. Jittery/Wobbly Hum (Simulate bad singing)
    # Pitch vibrato + Timing errors
    jittery_song = np.concatenate([generate_tone(f, 0.5, sr) for f in [261, 329, 392, 523]])
    
    # Add Vibrato (FM synthesis)
    t = np.linspace(0, len(jittery_song)/sr, len(jittery_song))
    vibrato = 0.5 * np.sin(2 * np.pi * 5 * t) # 5Hz vibrato
    # We can't easily FM modulate the existing array, so let's just add noise to simulate timbre variance
    jittery_hum = jittery_song + np.random.normal(0, 0.05, jittery_song.shape)
    
    # Slight time stretch
    jittery_hum = scipy_signal.resample(jittery_hum, int(len(jittery_hum) * 1.1))
    
    print("\nComparing Jittery/Impure Hum...")
    score_jitter = ap.compare_audio(jittery_hum, jittery_song)
    print(f"Jittery Hum Score: {score_jitter}% (Should be decent, > 60%)")
    
    # 4. Compare (Mismatch Expected)
    # Different melody: F4, A4, C5, E5
    random_song = np.concatenate([
        generate_tone(349.23, note_duration, sr), 
        generate_tone(440.00, note_duration, sr), 
        generate_tone(523.25, note_duration, sr), 
        generate_tone(659.25, note_duration, sr), 
    ])
    
    print("\nComparing Mismatch...")
    score_mismatch = ap.compare_audio(hum_noisy, random_song)
    print(f"MISMATCH SCORE: {score_mismatch}%")

if __name__ == "__main__":
    test_humming_logic()
