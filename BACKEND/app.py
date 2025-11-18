import json
import os
import subprocess
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_BINARY = BASE_DIR / "automata_sim.exe"
AUTOMATA_SIM_PATH = Path(os.environ.get("AUTOMATA_SIM_PATH", DEFAULT_BINARY))

app = Flask(__name__)


class BackendConfigError(RuntimeError):
    pass


def ensure_binary_available() -> None:
    if not AUTOMATA_SIM_PATH.exists():
        raise BackendConfigError(
            f"Automata simulator binary not found at {AUTOMATA_SIM_PATH}. "
            "Set AUTOMATA_SIM_PATH env var or copy automata_sim.exe here."
        )


def build_command(payload: dict, dataset_path: str, automaton_dump_path: str) -> list[str]:
    mode = payload.get("mode", "auto").lower()
    if mode not in {"auto", "nfa", "dfa", "efa", "pda"}:
        raise BackendConfigError(f"Unsupported mode '{mode}'.")

    cmd = [str(AUTOMATA_SIM_PATH)]

    pattern = payload.get("pattern", "")
    if pattern:
        cmd += ["--pattern", pattern]

    if payload.get("trace"):
        cmd.append("--trace")

    mismatch_budget = payload.get("mismatch_budget")
    if mismatch_budget is not None:
        cmd += ["--k", str(mismatch_budget)]

    if payload.get("allow_dot_bracket"):
        cmd.append("--dot-bracket")

    if mode != "auto":
        cmd += ["--mode", mode]

    if dataset_path:
        cmd += ["--input", dataset_path]

    cmd += ["--dump-automaton", automaton_dump_path]
    return cmd


def write_sequences_to_tempfile(sequences: list[str]) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    try:
        for seq in sequences:
            tmp.write(seq.strip() + "\n")
    finally:
        tmp.close()
    return tmp.name


@app.route("/simulate", methods=["POST"])
def simulate():
    ensure_binary_available()

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

    automaton_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    automaton_file.close()

    try:
        cmd = build_command(payload, dataset_path, automaton_file.name)
    except BackendConfigError as exc:
        if temp_dataset_path:
            os.unlink(temp_dataset_path)
        os.unlink(automaton_file.name)
        return jsonify({"error": str(exc)}), 400

    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        if temp_dataset_path:
            os.unlink(temp_dataset_path)

    automaton_json = None
    try:
        with open(automaton_file.name, "r", encoding="utf-8") as dump:
            automaton_json = json.load(dump)
    except json.JSONDecodeError as exc:
        automaton_json = {"error": f"Failed to decode automaton dump: {exc}"}
    finally:
        os.unlink(automaton_file.name)

    response_body = {
        "command": cmd,
        "return_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "automaton": automaton_json,
    }

    status = 200 if completed.returncode == 0 else 500
    return jsonify(response_body), status


@app.route("/healthz", methods=["GET"])
def healthz():
    exists = AUTOMATA_SIM_PATH.exists()
    return jsonify({"status": "ok" if exists else "binary-missing", "binary": str(AUTOMATA_SIM_PATH)})


if __name__ == "__main__":
    ensure_binary_available()
    app.run(debug=True)

