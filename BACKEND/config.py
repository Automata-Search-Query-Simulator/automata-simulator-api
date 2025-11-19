"""Configuration module for automata simulator API."""
import os
import platform
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
# Platform-specific binary name: Windows uses .exe, macOS/Linux don't
if platform.system() == "Windows":
    DEFAULT_BINARY = BASE_DIR / "automata_sim.exe"
else:
    DEFAULT_BINARY = BASE_DIR / "automata_sim"
AUTOMATA_SIM_PATH = Path(os.environ.get("AUTOMATA_SIM_PATH", DEFAULT_BINARY))


class BackendConfigError(RuntimeError):
    """Exception raised for configuration errors."""


def ensure_binary_available() -> None:
    """Ensure the automata simulator binary is available."""
    if not AUTOMATA_SIM_PATH.exists():
        binary_name = "automata_sim.exe" if platform.system() == "Windows" else "automata_sim"
        other_binary = BASE_DIR / ("automata_sim.exe" if platform.system() != "Windows" else "automata_sim")
        
        error_msg = (
            f"Automata simulator binary not found at {AUTOMATA_SIM_PATH}. "
            f"Set AUTOMATA_SIM_PATH env var or copy {binary_name} here."
        )
        
        # Check if the wrong platform's binary exists
        if other_binary.exists():
            current_platform = platform.system()
            error_msg += (
                f" Note: Found {other_binary.name} (for {('Windows' if current_platform != 'Windows' else 'macOS/Linux')}), "
                f"but you need {binary_name} for {current_platform}."
            )
        
        raise BackendConfigError(error_msg)

