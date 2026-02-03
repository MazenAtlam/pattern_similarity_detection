import sys
import os
import numpy as np
import librosa

# Adjust path to find src/backend
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)

from api.services.audio_processor import AudioProcessor

def generate_polyphonic_song(duration=5.0, sr=22050):
    """Generates a song with melody + noise + background chords."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    
    # 1. Melody (Simple sine)
    # C4 -> E4 -> G4 (arpeggio)
    melody = np.zeros_like(t)
    # First third
    idx1 = int(len(t)/3)
    idx2 = int(2*len(t)/3)
    
    melody[:idx1] = np.sin(2 * np.pi * 261.63 * t[:idx1])
    melody[idx1:idx2] = np.sin(2 * np.pi * 329.63 * t[idx1:idx2])
    melody[idx2:] = np.sin(2 * np.pi * 392.00 * t[idx2:])
    
    # 2. Background (Low drone + Noise)
    # Bass note (C3)
    bass = 0.3 * np.sin(2 * np.pi * 130.81 * t)
    # Noise (Simulate drums/percussion)
    noise = np.random.normal(0, 0.1, t.shape)
    
    # Mix
    full_song = melody + bass + noise
    return full_song, sr

def test_pitch_extraction():
    print("--- Testing Pitch Contour Feasibility ---")
    
    # 1. Generate Polyphonic Song
    song, sr = generate_polyphonic_song()
    print(f"Generated song duration: {len(song)/sr:.2f}s")
    
    # 2. Attempt Pitch Extraction (simulating what we'd do in the backend)
    # Use librosa.pyin (Probabilistic YIN) - standard for pitch tracking
    # fmin=note_to_hz('C2'), fmax=note_to_hz('C7')
    print("Extracting pitch (f0) using pyin...")
    
    # OPTION A: Raw
    f0_raw, voic, prob = librosa.pyin(song, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), sr=sr)
    
    # OPTION B: Harmonic extraction first (Mocking 'audio_processor' hpss logic)
    y_harm, y_perc = librosa.effects.hpss(song)
    f0_harm, _, _ = librosa.pyin(y_harm, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), sr=sr)
    
    # Check coverage (how many frames tracked pitch?)
    coverage_raw = np.sum(~np.isnan(f0_raw)) / len(f0_raw)
    coverage_harm = np.sum(~np.isnan(f0_harm)) / len(f0_harm)
    
    print(f"Pitch Coverage (Raw Average): {coverage_raw:.2%}")
    print(f"Pitch Coverage (Harmonic Only): {coverage_harm:.2%}")
    
    # Check accuracy (Did it find C4=261, E4=329, G4=392?)
    # We'll check the median pitch of the detected segments
    
    valid_f0 = f0_harm[~np.isnan(f0_harm)]
    if len(valid_f0) > 0:
        median_pitch = np.median(valid_f0)
        print(f"Median Detected Pitch: {median_pitch:.2f} Hz")
        # Average of 261, 329, 392 is ~327 Hz. 
        # If it tracked Bass (130 Hz), median would be low.
        
        if 250 < median_pitch < 400:
             print("✅ Success: Tracked Melody range.")
        elif median_pitch < 200:
             print("⚠️  Warning: Tracked Bass/Background.")
        else:
             print("❓ Unknown range.")
             
    else:
        print("❌ Failure: No pitch detected.")

if __name__ == "__main__":
    test_pitch_extraction()
