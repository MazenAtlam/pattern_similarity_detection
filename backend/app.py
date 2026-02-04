from api import create_app
from flask import jsonify
app = create_app()

@app.route('/')
def health_check():
    return jsonify({
        "status": "online",
        "project": "Fourier Similarity Detector API"
    }), 200

import os
from flask import send_from_directory

# 1. robustly find the 'data/songs' folder relative to this file (app.py)
# app.py is in backend/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_FOLDER = os.path.join(BASE_DIR, 'data', 'songs')

# 2. Add the route to serve the files
@app.route('/static/songs/<path:filename>')
def serve_songs(filename):
    print(f"DEBUG: Request for song: {filename}")
    print(f"DEBUG: Looking in: {SONGS_FOLDER}")
    return send_from_directory(SONGS_FOLDER, filename)

if __name__ == '__main__':
    # Debug mode is on for development
    print("start...")
    app.run(debug=True, port=5000)