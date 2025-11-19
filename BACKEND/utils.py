"""Utility functions for automata simulator API."""
import tempfile

from config import AUTOMATA_SIM_PATH, BackendConfigError


def build_command(payload: dict, dataset_path: str) -> list[str]:
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

    # Note: --dump-automaton is not supported by the current binary version
    # The automaton structure would need to be extracted from stdout or
    # the feature added to the C++ binary
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

