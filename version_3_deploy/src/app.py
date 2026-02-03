from flask import Flask, request, jsonify
import sys
import os
import pickle
import numpy as np

# Add current dir to path to find local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pattern_matcher_v3 import FingerprintDatabaseV3

app = Flask(__name__)

# Initialize DB (pointing to shared V3 data)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'version_3_more_than_one_pass', 'data')

# In deployment, maybe data is local. For now, link to V3 data.
if not os.path.exists(DATA_DIR):
    # Fallback to local 'data' if deployed isolation
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

print(f"Loading database from {DATA_DIR}...")
db = FingerprintDatabaseV3(base_data_dir=DATA_DIR)

def seconds_to_mm_ss(seconds):
    """Converts seconds (float/int) to MM:SS string."""
    try:
        total_seconds = int(float(seconds))
        minutes = total_seconds // 60
        secs = total_seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    except:
        return "00:00"

@app.route('/api/v1/pass_sequences/detect', methods=['POST'])
def detect_pass_sequences():
    try:
        data = request.get_json()
        if not data or 'sequence_path' not in data:
            return jsonify({
                "status": "failed",
                "error": "Missing 'sequence_path' in request body"
            }), 400
            
        seq_path = data['sequence_path']
        
        # In a real scenario, 'sequence_path' might be a file on the server.
        # Check if file exists.
        # If absolute path is provided, use it. If relative, assume relative to ...?
        # Let's try to interpret it.
        
        real_path = seq_path
        if not os.path.exists(real_path):
             # Try relative to cwd or code root?
             # For testing purposes, valid path is expected.
             return jsonify({
                 "status": "failed",
                 "error": f"File not found: {seq_path}"
             }), 404
             
        # Load the sequence (Fingerprint)
        with open(real_path, 'rb') as f:
            query_sequence = pickle.load(f)
            
        # Determine length
        # Assuming query_sequence is a dict with 'length' or list of vectors
        length = query_sequence.get('length', 1)
        if 'vectors' in query_sequence:
            length = len(query_sequence.get('vectors', [])) or 1
            
        # Load appropriate DB level
        if db.current_length != length:
            db.load_level(length)
            
        # Search
        # query_sequence needs to match the structure expected by find_nearest_neighbors
        # (dict with 'vectors', 'teammates', 'opponents', 'game_id', 'timestamp')
        
        results = db.find_nearest_neighbors(query_sequence, top_k=5)
        
        formatted_results = []
        for r in results:
            # r has 'distance', 'data' (the match entry)
            entry = r['data']
            
            # Format events geometry
            # entry['vectors'] gives relative vectors.
            # entry['start_x'], 'start_y' is start.
            
            events_formatted = []
            curr_x, curr_y = entry['start_x'], entry['start_y']
            
            # Add Start
            events_formatted.append({"x": round(float(curr_x), 2), "y": round(float(curr_y), 2)})
            
            for vec in entry['vectors']:
                curr_x += vec[0]
                curr_y += vec[1]
                events_formatted.append({"x": round(float(curr_x), 2), "y": round(float(curr_y), 2)})
            
            formatted_results.append({
                "similarity_measure": round(float(r['distance']), 4), # Smaller is better in our Metric (0 is perfect)
                # Note: User might expect 0 to 1 similarity index?
                # "Similarity Index" usually 1 is perfect, 0 is bad.
                # Chamfer/Euclidean is a distance (0 is perfect/identical).
                # To convert to [0,1]: 1 / (1 + distance)?
                # The PDF example showed "0.94", "0.45" -> Suggests Similarity Score.
                # Let's convert: Score = 1 / (1 + distance/100)? Normalization is hard without bounds.
                # Or just return distance for now? The field name says "similarity_measure".
                # Usually measure can be distance. But example 0.94 implies score.
                # Let's do 1.0 / (1.0 + distance).
                "similarity_score": round(1.0 / (1.0 + float(r['distance'])), 4),
                "distance_metric": round(float(r['distance']), 4), # Keep both to be safe
                "sequence_start_time": seconds_to_mm_ss(entry['timestamp']),
                "sequence_events": events_formatted,
                "match_id": entry['game_id']
            })
            
        return jsonify({
            "status": "success",
            "matched_sequences_found": len(formatted_results),
            "pass_sequences_data": formatted_results
        })
        
    except Exception as e:
        return jsonify({
            "status": "failed",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
