from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/healthz')
@app.route('/simulate')
@app.route('/<path:path>')
def catch_all(path=''):
    return jsonify({
        "status": "api/index.py is loading!",
        "message": "Basic Flask is working, but BACKEND imports are disabled for testing",
        "path": path
    })
