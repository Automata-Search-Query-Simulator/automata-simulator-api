from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
@app.route("/test")
def test():
    return jsonify({"status": "ok", "message": "Basic Flask works!"})

