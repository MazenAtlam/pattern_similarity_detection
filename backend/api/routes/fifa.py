from flask import Blueprint, request, jsonify

fifa_bp = Blueprint('fifa', __name__)

@fifa_bp.route('/detect_by_metadata', methods=['POST'])
def detect_by_metadata():
    """
    Endpoint to find sequences by Player Name, Team, etc.
    """
    data = request.json
    return jsonify({
        "status": "success", 
        "message": f"Searching for sequence with metadata: {data}"
    }), 200

@fifa_bp.route('/detect_by_id', methods=['POST'])
def detect_by_id():
    """
    Endpoint to upload a sequence file and find matches.
    """
    return jsonify({
        "status": "success", 
        "message": "Sequence ID detection endpoint reachable"
    }), 200