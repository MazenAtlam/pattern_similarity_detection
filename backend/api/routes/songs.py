import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from api.services.audio_processor import AudioProcessor

songs_bp = Blueprint('songs', __name__)

# Initialize the processor
processor = AudioProcessor()

# --- Configuration ---
# Update this line to include 'webm'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm'}

# Define absolute paths for robustness
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'temp')
SONGS_DB_FOLDER = os.path.join(BASE_DIR, 'data', 'songs')

# Ensure directories exist (Create them if they don't)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SONGS_DB_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from api.services.audio_processor_v1 import AudioProcessorV1
from api.services.audio_processor_v2 import AudioProcessorV2
from api.services.audio_processor_v3 import AudioProcessorV3

@songs_bp.route('/detect', methods=['POST'])
def detect_song():
    """
    Receives an audio file (key: 'audio_data') and 'version' parameter.
    Saves file, compares using selected algorithm.
    """
    # 1. specific check for the file part
    if 'audio_data' not in request.files:
        return jsonify({"status": "failed", "error": "No audio file part. Key must be 'audio_data'"}), 400
    
    file = request.files['audio_data']
    
    if file.filename == '':
        return jsonify({"status": "failed", "error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        # Secure the filename and save to temp folder
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            # CHECK VERSION
            version = request.form.get('version', 'v0') # Default too v0
            
            if version == 'v1':
                current_processor = AudioProcessorV1()
                print("DEBUG: Using AudioProcessorV1 (Pitch Contour)")
            elif version == 'v2':
                current_processor = AudioProcessorV2()
                print("DEBUG: Using AudioProcessorV2 (Fast Spectrogram Pitch)")
            elif version == 'v3':
                current_processor = AudioProcessorV3()
                print("DEBUG: Using AudioProcessorV3 (Smart Fast Pitch - HPSS)")
            else:
                current_processor = processor # Default loaded instance
                print("DEBUG: Using AudioProcessor (Chroma CENS)")

            # 2. Load the user's 'humming'
            user_signal = current_processor.load_audio(filepath)
            
            results = []
            
            # 3. Check if we have any reference songs to compare against
            print(f"DEBUG: Searching for songs in: {SONGS_DB_FOLDER}")
            reference_songs = [f for f in os.listdir(SONGS_DB_FOLDER) if allowed_file(f)]
            
            if not reference_songs:
                os.remove(filepath)
                return jsonify({
                    "status": "success", 
                    "message": "No reference songs found in data/songs/. Please add .wav files to test.",
                    "results": []
                }), 200

            # 4. Loop through database songs and compare
            for song_file in reference_songs:
                song_path = os.path.join(SONGS_DB_FOLDER, song_file)
                
                # Load reference song
                db_signal = current_processor.load_audio(song_path)
                
                # Calculate Similarity
                similarity = current_processor.compare_audio(user_signal, db_signal)
                
                results.append({
                    "song_name": song_file,
                    "artist": "Unknown", 
                    "similarity_index": similarity,
                    "file_url": f"/static/songs/{song_file}" 
                })
            
            # 5. Sort results: Highest similarity first
            results.sort(key=lambda x: x['similarity_index'], reverse=True)
            
            # Cleanup: Remove the temp user file
            os.remove(filepath)
            
            return jsonify({
                "status": "success",
                "matched_songs_found": len(results),
                "results": results[:10]  # Return top 10
            }), 200
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(filepath):
                os.remove(filepath)
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"status": "failed", "error": str(e)}), 500
    
    return jsonify({"status": "failed", "error": "Invalid file type"}), 400