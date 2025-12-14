from flask import Flask, jsonify
from index import configure_cors

app = Flask(__name__)
# Configure CORS with centralized configuration
configure_cors(app)

@app.route("/")
@app.route("/test")
def test():
    return jsonify({"status": "ok", "message": "Basic Flask works!"})

