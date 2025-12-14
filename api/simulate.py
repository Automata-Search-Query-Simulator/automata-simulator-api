"""Simulate endpoint - connects to BACKEND automata simulator."""
import sys
import os
from pathlib import Path
from flask import Flask

app = Flask(__name__)

# Add BACKEND to path
backend_dir = Path(__file__).resolve().parent.parent / "BACKEND"
sys.path.insert(0, str(backend_dir))
os.environ["VERCEL"] = "1"

try:
    # Import the entire Flask app from BACKEND
    from app import app as backend_app
    
    # Replace our app with the backend app
    app = backend_app
    
except Exception as e:
    import traceback
    from flask import jsonify
    
    @app.route('/', methods=["GET", "POST"])
    @app.route('/api/simulate', methods=["GET", "POST"])
    def simulate():
        return jsonify({
            "error": "Failed to import BACKEND",
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "backend_dir": str(backend_dir),
            "sys_path": sys.path[:5]
        }), 500
