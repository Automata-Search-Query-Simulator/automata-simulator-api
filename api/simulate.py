"""Simulate endpoint for Vercel - uses exact same logic as BACKEND/app.py"""
import json
import logging
import os
import subprocess
import sys
import traceback
from pathlib import Path
from urllib.parse import unquote

from flask import Flask, jsonify, request

# Add BACKEND to path so we can import from it
backend_dir = Path(__file__).resolve().parent.parent / "BACKEND"
sys.path.insert(0, str(backend_dir))
os.environ["VERCEL"] = "1"

# Import BACKEND modules
from config import AUTOMATA_SIM_PATH, BackendConfigError, ensure_binary_available
from logger import get_logger
from parser import parse_stdout
from utils import build_command, write_sequences_to_tempfile, create_automaton_dump_file

app = Flask(__name__)
logger = get_logger()

@app.route('/', methods=["GET"])
@app.route('/api/simulate', methods=["GET"])
def simulate():
    try:
        try:
            ensure_binary_available()
        except BackendConfigError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            return jsonify({"error": "Binary check failed", "message": str(exc), "type": type(exc).__name__}), 500

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
            "rna_mode": request.args.get("rna_mode", "").lower() in ("true", "1", "yes"),
            "secondary_structure_path": request.args.get("secondary_structure_path"),
            "secondary_structures": request.args.getlist("secondary_structures"),  # Inline dot-bracket notation
        }

        dataset_path = payload.get("input_path")
        temp_dataset_path = None
        temp_secondary_path = None
        automaton_dump_path = None
        mode = payload.get("mode", "auto").lower()
        
        if not dataset_path:
            sequences = payload.get("sequences")
            if sequences:
                temp_dataset_path = write_sequences_to_tempfile(sequences)
                dataset_path = temp_dataset_path
        
        # Handle inline secondary structures (dot-bracket notation)
        secondary_structure_path = payload.get("secondary_structure_path")
        if not secondary_structure_path:
            secondary_structures = payload.get("secondary_structures")
            if secondary_structures:
                temp_secondary_path = write_sequences_to_tempfile(secondary_structures)
                secondary_structure_path = temp_secondary_path
        
        # Add secondary structure path to payload for command builder
        payload["secondary_structure_path"] = secondary_structure_path

        # Create temp file for automaton dump if the selected mode supports it
        # (NFA, DFA, EFA, PDA). AUTO mode doesn't specify which automaton is built.
        if mode in {"nfa", "dfa", "efa", "pda"}:
            automaton_dump_path = create_automaton_dump_file()

        try:
            cmd = build_command(payload, dataset_path, automaton_dump_path)
        except BackendConfigError as exc:
            if temp_dataset_path:
                os.unlink(temp_dataset_path)
            if temp_secondary_path:
                os.unlink(temp_secondary_path)
            if automaton_dump_path and os.path.exists(automaton_dump_path):
                os.unlink(automaton_dump_path)
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
                timeout=30,  # 30 second timeout for Vercel
            )
            
            # Log execution result when in debug mode
            if app.debug or os.environ.get("FLASK_DEBUG", "").lower() in ("true", "1", "yes"):
                logger.debug(f"Command return code: {completed.returncode}")
                if completed.stdout:
                    logger.debug(f"Command stdout (first 500 chars): {completed.stdout[:500]}")
                if completed.stderr:
                    logger.debug(f"Command stderr: {completed.stderr}")
            
            # If command failed and it's due to unsupported --dump-automaton flag, retry without it
            if (completed.returncode != 0 and automaton_dump_path and 
                "--dump-automaton" in " ".join(cmd) and
                ("Unknown or incomplete argument" in completed.stderr or 
                 "unknown" in completed.stderr.lower() and "dump-automaton" in completed.stderr.lower())):
                logger.warning("Binary doesn't support --dump-automaton flag, retrying without it")
                # Clean up the dump file since we're not using it
                if os.path.exists(automaton_dump_path):
                    os.unlink(automaton_dump_path)
                # Remove --dump-automaton flag and retry
                cmd_without_dump = [arg for arg in cmd if arg != "--dump-automaton" and arg != automaton_dump_path]
                completed = subprocess.run(
                    cmd_without_dump,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )
                # Clear automaton_dump_path since we're not using it
                automaton_dump_path = None
                if app.debug or os.environ.get("FLASK_DEBUG", "").lower() in ("true", "1", "yes"):
                    logger.debug(f"Retry command return code: {completed.returncode}")
        except subprocess.TimeoutExpired:
            if temp_dataset_path:
                os.unlink(temp_dataset_path)
            if temp_secondary_path:
                os.unlink(temp_secondary_path)
            if automaton_dump_path and os.path.exists(automaton_dump_path):
                os.unlink(automaton_dump_path)
            return jsonify({"error": "Simulation timed out (>30s)"}), 500
        except Exception as e:
            if temp_dataset_path:
                os.unlink(temp_dataset_path)
            if temp_secondary_path:
                os.unlink(temp_secondary_path)
            if automaton_dump_path and os.path.exists(automaton_dump_path):
                os.unlink(automaton_dump_path)
            return jsonify({"error": "Execution failed", "message": str(e), "type": type(e).__name__}), 500
        finally:
            if temp_dataset_path:
                os.unlink(temp_dataset_path)
            if temp_secondary_path:
                os.unlink(temp_secondary_path)

        # Parse stdout into structured JSON
        if completed.returncode == 0:
            # Debug: Log raw stdout when in debug mode
            if app.debug or os.environ.get("FLASK_DEBUG", "").lower() in ("true", "1", "yes"):
                logger.debug(f"Raw stdout from C++ binary:\n{completed.stdout}")
            
            parsed_result = parse_stdout(completed.stdout)
            
            # Load automaton structure from dump file if it exists
            # Works for NFA, DFA, EFA, and PDA modes (if binary supports --dump-automaton)
            if automaton_dump_path and os.path.exists(automaton_dump_path):
                try:
                    with open(automaton_dump_path, "r", encoding="utf-8") as f:
                        automaton_data = json.load(f)
                        parsed_result["automaton"] = automaton_data
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Failed to read automaton dump file: {e}")
                finally:
                    # Clean up automaton dump file
                    if os.path.exists(automaton_dump_path):
                        os.unlink(automaton_dump_path)
            
            return jsonify(parsed_result), 200
        else:
            # Clean up automaton dump file and temp secondary file on error
            if automaton_dump_path and os.path.exists(automaton_dump_path):
                os.unlink(automaton_dump_path)
            if temp_secondary_path and os.path.exists(temp_secondary_path):
                os.unlink(temp_secondary_path)
            return jsonify({
                "error": "Simulation failed",
                "stderr": completed.stderr,
                "stdout": completed.stdout[:500] if completed.stdout else "",
                "returncode": completed.returncode,
                "command": " ".join(cmd)
            }), 500
    except Exception as e:
        # Catch any unhandled exception
        return jsonify({
            "error": "Unhandled exception in /simulate",
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }), 500
