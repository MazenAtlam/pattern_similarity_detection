from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Enable CORS to allow requests from your React Frontend
    CORS(app, resources={r"/*": {"origins": "*"}}) 
    
    # Register Blueprints
    from api.routes.songs import songs_bp
    from api.routes.fifa import fifa_bp
    
    app.register_blueprint(songs_bp, url_prefix='/api/v1/songs')
    app.register_blueprint(fifa_bp, url_prefix='/api/v1/pass_sequences')
    
    return app