"""
Bash Executor Node for ComfyUI
Executes a bash command and returns a JSON-compatible container with the result
or an error message on failure.
"""

import subprocess
import json

# Local imports
from .common import any_typ


class mbBash:
    """Execute a bash command and return the result as a JSON-compatible object."""

    DEFAULT_CMD = 'echo "{\"result\": \"ok\"}"'

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "cmd": ("STRING", {
                    "default": cls.DEFAULT_CMD,
                    "multiline": True,
                    "tooltip": "Bash command to execute. Will be run with /bin/bash -lc"
                })
            }
        }

    TITLE = "Bash Executor"
    RETURN_TYPES = (any_typ, "STRING")
    RETURN_NAMES = ("result", "error")
    FUNCTION = "execute"
    CATEGORY = "unset"
    DESCRIPTION = "Execute a bash command and return a JSON-like result container on 'result', or an error string on 'error'."

    def execute(self, cmd: str):
        """Run the provided bash command and return (result, error).

        - If the command exits with non-zero status, returns (None, error_message).
        - If the command exits successfully and stdout is valid JSON, returns (parsed_json, None).
        - Otherwise returns (dict with stdout/stderr/returncode, None).
        """
        if cmd is None or cmd == "":
            cmd = self.DEFAULT_CMD

        try:
            proc = subprocess.run(["/bin/bash", "-lc", cmd], capture_output=True, text=True)
        except Exception as e:
            return (None, str(e))

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        returncode = proc.returncode

        # If non-zero exit, return error (include stderr or stdout)
        if returncode != 0:
            msg = f"Exit {returncode}: {stderr.strip() or stdout.strip()}"
            return (None, msg)

        # Successful exit: try to parse stdout as JSON
        stdout_str = stdout.strip()
        if stdout_str == "":
            # Empty output, return a minimal JSON container
            return ({"stdout": "", "stderr": stderr, "returncode": returncode}, None)

        try:
            parsed = json.loads(stdout_str)
            return (parsed, None)
        except Exception:
            # Not valid JSON — return a container with raw outputs
            return ({"stdout": stdout, "stderr": stderr, "returncode": returncode}, None)

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Force execution each time
        import random
        return random.randint(0, 32768)
