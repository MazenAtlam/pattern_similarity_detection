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

@songs_bp.route('/detect', methods=['POST'])
def detect_song():
    """
    Receives an audio file (key: 'audio_data'), saves it, 
    and compares it against all songs in data/songs/.
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
            # 2. Load the user's 'humming'
            user_signal = processor.load_audio(filepath)
            
            results = []
            
            # 3. Check if we have any reference songs to compare against
            print(f"DEBUG: Searching for songs in: {SONGS_DB_FOLDER}") # <--- Add this line
            reference_songs = [f for f in os.listdir(SONGS_DB_FOLDER) if allowed_file(f)]
            print(f"DEBUG: Found songs: {reference_songs}") 
            
            if not reference_songs:
                # If no songs in DB, return a helpful message
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
                # (Note: In a real production app, we would cache these features to avoid re-loading)
                db_signal = processor.load_audio(song_path)
                
                # Calculate Similarity
                similarity = processor.compare_audio(user_signal, db_signal)
                
                results.append({
                    "song_name": song_file,
                    "artist": "Unknown", # We'd need a metadata DB for this
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
                "results": results[:5]  # Return top 5
            }), 200
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"status": "failed", "error": str(e)}), 500
    
    return jsonify({"status": "failed", "error": "Invalid file type"}), 400