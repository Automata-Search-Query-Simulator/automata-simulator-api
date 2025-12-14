from flask import Flask, jsonify
from index import configure_cors

app = Flask(__name__)
# Configure CORS with centralized configuration
configure_cors(app)

@app.route('/')
@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello from Vercel!", "status": "ok"})

