"""Simulate endpoint - Full implementation."""
from flask import Flask, jsonify, request
import sys
import os
from pathlib import Path
import traceback

app = Flask(__name__)

# Add BACKEND to path
backend_dir = Path(__file__).resolve().parent.parent / "BACKEND"
sys.path.insert(0, str(backend_dir))
os.environ["VERCEL"] = "1"

# Import BACKEND modules
from config import AUTOMATA_SIM_PATH, BackendConfigError, ensure_binary_available
from logger import get_logger
from parser import parse_stdout
from utils import build_command, write_sequences_to_tempfile, create_automaton_dump_file
import subprocess
import json

logger = get_logger()

@app.route('/', methods=["GET"])
@app.route('/api/simulate', methods=["GET"])
def simulate():
    try:
        # Check binary
        try:
            ensure_binary_available()
        except BackendConfigError as exc:
            return jsonify({"error": str(exc)}), 400

        # Get parameters
        payload = {
            "input_path": request.args.get("input_path"),
            "sequences": request.args.getlist("sequences"),
            "mode": request.args.get("mode", "auto"),
            "pattern": request.args.get("pattern", ""),
            "mismatch_budget": request.args.get("mismatch_budget", type=int),
            "allow_dot_bracket": request.args.get("allow_dot_bracket", "").lower() in ("true", "1", "yes"),
            "rna_mode": request.args.get("rna_mode", "").lower() in ("true", "1", "yes"),
        }

        # Handle sequences
        dataset_path = payload.get("input_path")
        temp_dataset_path = None
        
        if not dataset_path:
            sequences = payload.get("sequences")
            if sequences:
                temp_dataset_path = write_sequences_to_tempfile(sequences)
                dataset_path = temp_dataset_path

        # Ensure binary is executable
        import stat
        if not os.access(str(AUTOMATA_SIM_PATH), os.X_OK):
            os.chmod(str(AUTOMATA_SIM_PATH), os.stat(str(AUTOMATA_SIM_PATH)).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        # Build command
        cmd = build_command(payload, dataset_path, None)

        # Execute
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )

        # Cleanup
        if temp_dataset_path:
            os.unlink(temp_dataset_path)

        # Parse results
        if completed.returncode == 0:
            parsed_result = parse_stdout(completed.stdout)
            return jsonify(parsed_result), 200
        else:
            return jsonify({
                "error": "Simulation failed",
                "stderr": completed.stderr,
                "returncode": completed.returncode
            }), 500

    except Exception as e:
        return jsonify({
            "error": "Exception in simulate",
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }), 500
