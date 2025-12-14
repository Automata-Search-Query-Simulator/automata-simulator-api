from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello from Vercel!", "status": "ok"})

