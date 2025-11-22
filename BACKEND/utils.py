"""Utility functions for automata simulator API."""
import tempfile

from config import AUTOMATA_SIM_PATH, BackendConfigError


def build_command(payload: dict, dataset_path: str, automaton_dump_path: str = None) -> list[str]:
    """Build command list for automata simulator binary."""
    mode = payload.get("mode", "auto").lower()
    if mode not in {"auto", "nfa", "dfa", "efa", "pda"}:
        raise BackendConfigError(f"Unsupported mode '{mode}'.")

    cmd = [str(AUTOMATA_SIM_PATH)]

    pattern = payload.get("pattern", "")
    if pattern:
        cmd += ["--pattern", pattern]

    mismatch_budget = payload.get("mismatch_budget")
    if mismatch_budget is not None:
        cmd += ["--k", str(mismatch_budget)]

    if payload.get("allow_dot_bracket"):
        cmd.append("--dot-bracket")

    if mode != "auto":
        cmd += ["--mode", mode]

    if dataset_path:
        cmd += ["--input", dataset_path]

    # Add --dump-automaton flag if dump path is provided and mode supports it
    # Note: This will work if the binary supports it, otherwise it will be ignored
    # and the automaton data simply won't be included in the response
    if automaton_dump_path and mode in {"nfa", "dfa", "efa", "pda"}:
        cmd += ["--dump-automaton", automaton_dump_path]

    return cmd


def write_sequences_to_tempfile(sequences: list[str]) -> str:
    """Write sequences to a temporary file and return the file path."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    try:
        for seq in sequences:
            tmp.write(seq.strip() + "\n")
    finally:
        tmp.close()
    return tmp.name


def create_automaton_dump_file() -> str:
    """Create a temporary file for automaton dump and return the file path."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
    tmp.close()
    return tmp.name

