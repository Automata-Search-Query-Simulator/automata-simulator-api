from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Configure CORS - allow frontend origin
CORS(app, origins=["https://automata-simulator-web.vercel.app", "http://localhost:3000"])

@app.route('/')
@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello from Vercel!", "status": "ok"})

