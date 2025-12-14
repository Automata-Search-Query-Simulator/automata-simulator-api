from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Configure CORS - allow frontend origin
CORS(app, origins=["https://automata-simulator-web.vercel.app", "http://localhost:3000"])

@app.route('/')
@app.route('/api')
@app.route('/api/')
@app.route('/api/index')
def index():
    return jsonify({
        "status": "api/index.py is working!",
        "message": "Basic Flask is working, BACKEND imports disabled for testing"
    })
