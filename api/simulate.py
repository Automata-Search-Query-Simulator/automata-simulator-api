from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/api/simulate')
def simulate():
    return jsonify({"status": "simulate endpoint", "message": "BACKEND not connected yet"})

