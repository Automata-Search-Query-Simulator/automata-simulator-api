"""Vercel serverless function entry point."""
from flask import Flask, jsonify
import sys
import os
from pathlib import Path
import traceback

app = Flask(__name__)

# Try to add BACKEND to path and import
error_info = None
try:
    backend_dir = Path(__file__).resolve().parent.parent / "BACKEND"
    sys.path.insert(0, str(backend_dir))
    os.environ["VERCEL"] = "1"
    
    # Try importing step by step to see what fails
    from config import AUTOMATA_SIM_PATH, BackendConfigError, ensure_binary_available
    from logger import get_logger
    from parser import parse_stdout
    from utils import build_command, write_sequences_to_tempfile, create_automaton_dump_file
    from app import app as backend_app
    
    # If imports succeed, use the backend app
    app = backend_app
    
except Exception as e:
    # If import fails, capture the error
    error_info = {
        "error": "Failed to import BACKEND modules",
        "message": str(e),
        "type": type(e).__name__,
        "traceback": traceback.format_exc(),
        "backend_dir": str(backend_dir) if 'backend_dir' in locals() else "not set",
        "sys_path": sys.path[:5]
    }

# If there was an import error, create routes that show it
if error_info:
    @app.route('/')
    @app.route('/<path:path>')
    def show_error(path=''):
        return jsonify(error_info), 500
