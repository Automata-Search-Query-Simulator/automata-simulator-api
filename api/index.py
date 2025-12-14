from flask import Flask, jsonify
from flask_cors import CORS

# Centralized CORS configuration - import this function in other API files
ALLOWED_ORIGINS = [
    "https://automata-simulator-web.vercel.app",
    "http://localhost:3000",
]


def configure_cors(app):
    """Configure CORS for a Flask app with centralized allowed origins."""
    CORS(app, origins=ALLOWED_ORIGINS)


app = Flask(__name__)
# Configure CORS with centralized configuration
configure_cors(app)

@app.route('/')
@app.route('/api')
@app.route('/api/')
@app.route('/api/index')
def index():
    return jsonify({
        "status": "api/index.py is working!",
        "message": "Basic Flask is working, BACKEND imports disabled for testing"
    })
