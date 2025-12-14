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

# On Vercel, includeFiles may nest assets under the function's folder.
# Try alternate locations if the default path doesn't exist.
def _resolve_binary_path() -> Path:
    candidate_paths = [AUTOMATA_SIM_PATH]
    try:
        # Path relative to api function directory (when packed with includeFiles)
        api_dir = Path(__file__).resolve().parent.parent / "api"
        candidate_paths.append(api_dir / "BACKEND" / ("automata_sim.exe" if platform.system() == "Windows" else "automata_sim"))
        # Project root BACKEND (when executed from different CWD)
        project_root = BASE_DIR.parent
        candidate_paths.append(project_root / "BACKEND" / ("automata_sim.exe" if platform.system() == "Windows" else "automata_sim"))
    except Exception:
        pass
    for p in candidate_paths:
        if p and Path(p).exists():
            return Path(p)
    return AUTOMATA_SIM_PATH

AUTOMATA_SIM_PATH = _resolve_binary_path()


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
    
    # Ensure binary is executable on Unix-like systems
    if platform.system() != "Windows":
        import stat
        current_permissions = os.stat(AUTOMATA_SIM_PATH).st_mode
        if not (current_permissions & stat.S_IXUSR):
            try:
                os.chmod(AUTOMATA_SIM_PATH, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            except (OSError, PermissionError):
                # If we can't set permissions, it might work anyway
                pass

