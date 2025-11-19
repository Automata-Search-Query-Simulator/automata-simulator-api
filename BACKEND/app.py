import logging
import os
import subprocess
from urllib.parse import unquote

from flask import Flask, jsonify, request

from config import AUTOMATA_SIM_PATH, BackendConfigError, ensure_binary_available
from logger import get_logger
from parser import parse_stdout
from utils import build_command, write_sequences_to_tempfile

app = Flask(__name__)
logger = get_logger()


@app.route("/simulate", methods=["GET"])
def simulate():
    try:
        ensure_binary_available()
    except BackendConfigError as exc:
        return jsonify({"error": str(exc)}), 400

    # Extract parameters from query string
    # For input_path, manually parse from raw query string to preserve '+' characters
    # Flask's args.get() uses unquote_plus() which converts '+' to spaces
    input_path_value = None
    query_string = request.query_string.decode("utf-8")
    if "input_path=" in query_string:
        # Find the input_path parameter and extract its value
        start_idx = query_string.find("input_path=") + len("input_path=")
        # Find the end - either next & or end of string
        end_idx = query_string.find("&", start_idx)
        if end_idx == -1:
            end_idx = len(query_string)
        # Extract and decode using unquote() to preserve '+' (not unquote_plus())
        encoded_value = query_string[start_idx:end_idx]
        input_path_value = unquote(encoded_value) if encoded_value else None
    
    payload = {
        "input_path": input_path_value if input_path_value is not None else request.args.get("input_path"),
        "sequences": request.args.getlist("sequences"),  # Get list of repeated parameters
        "mode": request.args.get("mode", "auto"),
        "pattern": request.args.get("pattern", ""),
        "mismatch_budget": request.args.get("mismatch_budget", type=int),
        "allow_dot_bracket": request.args.get("allow_dot_bracket", "").lower() in ("true", "1", "yes"),
    }

    dataset_path = payload.get("input_path")
    temp_dataset_path = None
    if not dataset_path:
        sequences = payload.get("sequences")
        if sequences:
            temp_dataset_path = write_sequences_to_tempfile(sequences)
            dataset_path = temp_dataset_path

    try:
        cmd = build_command(payload, dataset_path)
    except BackendConfigError as exc:
        if temp_dataset_path:
            os.unlink(temp_dataset_path)
        return jsonify({"error": str(exc)}), 400

    # Log command when in debug mode
    if app.debug or os.environ.get("FLASK_DEBUG", "").lower() in ("true", "1", "yes"):
        logger.debug(f"Executing command: {' '.join(cmd)}")
        logger.debug(f"Command arguments: {cmd}")

    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        
        # Log execution result when in debug mode
        if app.debug or os.environ.get("FLASK_DEBUG", "").lower() in ("true", "1", "yes"):
            logger.debug(f"Command return code: {completed.returncode}")
            if completed.stdout:
                logger.debug(f"Command stdout (first 500 chars): {completed.stdout[:500]}")
            if completed.stderr:
                logger.debug(f"Command stderr: {completed.stderr}")
    finally:
        if temp_dataset_path:
            os.unlink(temp_dataset_path)

    # Parse stdout into structured JSON
    if completed.returncode == 0:
        parsed_result = parse_stdout(completed.stdout)
        return jsonify(parsed_result), 200
    else:
        return jsonify({"error": "Simulation failed", "stderr": completed.stderr}), 500


@app.route("/healthz", methods=["GET"])
def healthz():
    exists = AUTOMATA_SIM_PATH.exists()
    return jsonify({"status": "ok" if exists else "binary-missing", "binary": str(AUTOMATA_SIM_PATH)})


if __name__ == "__main__":
    ensure_binary_available()
    # Set Flask debug mode and update logger level accordingly
    os.environ["FLASK_DEBUG"] = "true"
    logger.setLevel(logging.DEBUG)
    app.run(debug=True)

