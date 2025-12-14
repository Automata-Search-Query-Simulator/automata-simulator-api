from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/api/healthz')
def healthz():
    return jsonify({"status": "ok", "message": "Health check passed!"})

