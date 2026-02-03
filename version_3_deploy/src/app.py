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
        n_passes = data.get('number_of_passes', 1)
        play_idx = data.get('current_play_index', 0)
        
        # Check file
        if not os.path.exists(seq_path):
             return jsonify({
                 "status": "failed",
                 "error": f"File not found: {seq_path}"
             }), 404
             
        # Load the sequence data
        with open(seq_path, 'rb') as f:
            loaded_data = pickle.load(f)
            
        # Handle List vs Single Object
        query_sequence = None
        if isinstance(loaded_data, list):
            if 0 <= play_idx < len(loaded_data):
                query_sequence = loaded_data[play_idx]
            else:
                 return jsonify({
                    "status": "failed",
                    "error": f"Index {play_idx} out of bounds (Size: {len(loaded_data)})"
                 }), 400
        else:
            # Assume it's the object itself if not a list
            query_sequence = loaded_data
            
        # Ensure correct DB level is loaded
        if db.current_length != n_passes:
            db.load_level(n_passes)
            
        # Search
        results = db.find_nearest_neighbors(query_sequence, top_k=5)
        
        if not results:
             return jsonify({
                "status": "failed",
                "error": "No sequence found"
            })
        
        formatted_results = []
        for r in results:
            entry = r['data']
            
            # Reconstruct absolute events from start + vectors
            events_formatted = []
            curr_x, curr_y = entry['start_x'], entry['start_y']
            
            # 1. Start Point
            events_formatted.append({"x": round(float(curr_x), 2), "y": round(float(curr_y), 2)})
            
            # 2. Subsequent Points
            for vec in entry['vectors']:
                curr_x += vec[0]
                curr_y += vec[1]
                events_formatted.append({"x": round(float(curr_x), 2), "y": round(float(curr_y), 2)})
            
            formatted_results.append({
                "similarity_measure": round(1.0 / (1.0 + float(r['distance'])), 4), # Normalized Score? Or just distance?
                # User example showed 0.94. I'll stick to a normalized score format: 1/(1+dist).
                # If they want raw distance, I can swap. 
                # Let's match the "0.94" vibe.
                "sequence_start_time": seconds_to_mm_ss(entry['timestamp']),
                "sequence_events": events_formatted
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

@app.route('/api/v1/pass_sequences/count', methods=['POST'])
def get_sequence_count():
    try:
        data = request.get_json()
        if not data or 'sequence_path' not in data:
             return jsonify({"status": "failed", "error": "Missing sequence_path"}), 400
             
        seq_path = data['sequence_path']
        if not os.path.exists(seq_path):
             return jsonify({"status": "failed", "error": f"File not found: {seq_path}"}), 404
             
        # Load pickle to get Match ID and Length
        with open(seq_path, 'rb') as f:
            content = pickle.load(f)
            
        # Handle list or dict
        query = content[0] if isinstance(content, list) else content
        
        match_id = query.get('game_id')
        length = query.get('length', 1)
        
        if not match_id:
            return jsonify({"status": "failed", "error": "Could not determine match_id from file"}), 400
             
        # Load DB level
        if db.current_length != length:
            db.load_level(length)
            
        # Count
        count = 0
        for entry in db.database:
            if str(entry['game_id']) == str(match_id):
                count += 1
                
        return jsonify({
            "status": "success",
            "sequences_count": count
        })
        
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
