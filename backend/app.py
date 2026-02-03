from api import create_app
from flask import jsonify
app = create_app()

@app.route('/')
def health_check():
    return jsonify({
        "status": "online",
        "project": "Fourier Similarity Detector API"
    }), 200

if __name__ == '__main__':
    # Debug mode is on for development
    print("start...")
    app.run(debug=True, port=5000)