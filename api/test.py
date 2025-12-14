from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Configure CORS - allow frontend origin
CORS(app, origins=["https://automata-simulator-web.vercel.app", "http://localhost:3000"])

@app.route("/")
@app.route("/test")
def test():
    return jsonify({"status": "ok", "message": "Basic Flask works!"})

