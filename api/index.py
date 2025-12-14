from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/api')
@app.route('/api/')
@app.route('/api/index')
def index():
    return jsonify({
        "status": "api/index.py is working!",
        "message": "Basic Flask is working, BACKEND imports disabled for testing"
    })
