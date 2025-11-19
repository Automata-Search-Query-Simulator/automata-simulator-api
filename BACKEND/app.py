import os
import subprocess

from flask import Flask, jsonify, request

from config import AUTOMATA_SIM_PATH, BackendConfigError, ensure_binary_available
from parser import parse_stdout
from utils import build_command, write_sequences_to_tempfile

app = Flask(__name__)


@app.route("/simulate", methods=["POST"])
def simulate():
    try:
        ensure_binary_available()
    except BackendConfigError as exc:
        return jsonify({"error": str(exc)}), 400

    payload = request.get_json(force=True, silent=False)
    if payload is None:
        return jsonify({"error": "Invalid or missing JSON body."}), 400

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

    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
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
    app.run(debug=True)

