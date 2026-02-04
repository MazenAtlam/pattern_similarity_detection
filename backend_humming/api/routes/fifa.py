import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from api.services.pattern_matcher_v3 import FingerprintDatabaseV3

fifa_bp = Blueprint('fifa', __name__)

# Initialize DB (pointing to shared V3 data)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'fifa')

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

@fifa_bp.route('/detect', methods=['POST'])
def detect_pass_sequences():
    try:
        data = request.get_json()
        if not data or 'sequence_path' not in data:
            return jsonify({
                "status": "failed",
                "error": "Missing 'sequence_path' in request body"
            }), 400
            
        seq_path = data['sequence_path']
        
        # Try to infer n_passes from filename if not in body
        import re
        n_passes_req = data.get('number_of_passes')
        
        if n_passes_req:
             n_passes = int(n_passes_req)
        else:
             # Infer from filename
             filename = os.path.basename(seq_path)
             match = re.search(r'(\d+)pass\.pkl$', filename)
             if match:
                 n_passes = int(match.group(1))
             else:
                 # Last resort 
                 digits = re.findall(r'\d+', filename)
                 if digits:
                     n_passes = int(digits[-1])
                 else:
                     n_passes = 1 # Fallback default
        play_idx = data.get('current_play_index', 0)
        match_id_req = data.get('match_id')

        # Check file
        if not os.path.exists(seq_path):
             return jsonify({
                 "status": "failed",
                 "error": f"File not found: {seq_path}"
             }), 404
             
        # Ensure correct DB level is loaded
        if db.current_length != n_passes:
            db.load_level(n_passes)
            
        # Filter plays for this match
        # We assume db.database holds all plays for the current level (n_passes)
        if not match_id_req:
             # Fallback or error if match_id is mandatory? 
             # For backward compatibility maybe try to infer, but user explicitly said "request body has the match id"
             # Let's assume it's mandatory or we create an error.
             # Or if missing, maybe we just use the play_idx on the whole DB? 
             # Let's enforce match_id for correctness as per user intent.
             return jsonify({"status": "failed", "error": "Missing match_id in request"}), 400

        current_match_plays = [
            p for p in db.database
            if str(p['game_id']) == str(match_id_req)
        ]
        
        # Sort by timestamp to ensure consistent indexing
        current_match_plays.sort(key=lambda x: x['timestamp'])

        if not current_match_plays:
             return jsonify({
                "status": "failed",
                "error": f"No sequences found for match {match_id_req}"
            }), 404

        if 0 <= play_idx < len(current_match_plays):
            query_sequence = current_match_plays[play_idx]
        else:
             return jsonify({
                "status": "failed",
                "error": f"Index {play_idx} out of bounds (Size: {len(current_match_plays)})"
             }), 400
            
        # Search
        results = db.find_nearest_neighbors(query_sequence, top_k=10)
        
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
                "similarity_measure": round(1.0 / (1.0 + float(r['distance'])), 4), 
                "sequence_start_time": seconds_to_mm_ss(entry['timestamp']),
                "sequence_events": events_formatted
            })
            
        # Format query sequence for response
        query_events_formatted = []
        if query_sequence:
            qx, qy = query_sequence['start_x'], query_sequence['start_y']
            query_events_formatted.append({"x": round(float(qx), 2), "y": round(float(qy), 2)})
            for vec in query_sequence['vectors']:
                qx += vec[0]
                qy += vec[1]
                query_events_formatted.append({"x": round(float(qx), 2), "y": round(float(qy), 2)})

        return jsonify({
            "status": "success",
            "matched_sequences_found": len(formatted_results),
            "query_sequence_events": query_events_formatted,
            "pass_sequences_data": formatted_results
        })
        
    except Exception as e:
        return jsonify({
            "status": "failed",
            "error": str(e)
        }), 500

@fifa_bp.route('/count', methods=['POST'])
def get_sequence_count():
    try:
        data = request.get_json()
        if not data or 'sequence_path' not in data:
             return jsonify({"status": "failed", "error": "Missing sequence_path"}), 400
             
        seq_path = data['sequence_path']
        match_id = data.get('match_id')

        if not os.path.exists(seq_path):
             return jsonify({"status": "failed", "error": f"File not found: {seq_path}"}), 404
             
        if not match_id:
            return jsonify({"status": "failed", "error": "Missing match_id"}), 400
            
        # Infer length from filename (e.g. fingerprints_3pass.pkl)
        # Assuming format ends with "{number}pass.pkl"
        filename = os.path.basename(seq_path)
        import re
        match = re.search(r'(\d+)pass\.pkl$', filename)
        if match:
             length = int(match.group(1))
        else:
             # Fallback: maybe we assume default 1? or try to load?
             # Let's try to extract digits from filename if strict regex fails
             digits = re.findall(r'\d+', filename)
             if digits:
                 length = int(digits[-1]) # Take the last number likely to be the pass count
             else:
                 return jsonify({"status": "failed", "error": "Could not determine pass length from filename"}), 400
             
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