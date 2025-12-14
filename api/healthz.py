"""Health check endpoint."""
import sys
from pathlib import Path
from flask import Flask, jsonify

app = Flask(__name__)

# Add BACKEND to path
backend_dir = Path(__file__).resolve().parent.parent / "BACKEND"
sys.path.insert(0, str(backend_dir))

try:
    from config import AUTOMATA_SIM_PATH
    
    @app.route('/')
    @app.route('/api/healthz')
    def healthz():
        exists = AUTOMATA_SIM_PATH.exists()
        return jsonify({
            "status": "ok" if exists else "binary-missing",
            "binary": str(AUTOMATA_SIM_PATH),
            "exists": exists
        })
        
except Exception as e:
    @app.route('/')
    @app.route('/api/healthz')
    def healthz():
        return jsonify({
            "status": "error",
            "error": str(e),
            "message": "Failed to check binary"
        }), 500
