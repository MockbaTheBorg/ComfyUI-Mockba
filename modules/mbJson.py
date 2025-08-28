"""
JSON Selector Node for ComfyUI
Accepts a JSON-like input (dict/list or JSON string) and a dot-separated path
to select a sub-item. Returns a pretty-printed JSON string of the selected item
or an error message.
"""

import json as _json

from .common import any_typ


class mbJson:
    """Select and pretty-print part of a JSON object."""

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json": (any_typ, {
                    "tooltip": "Input JSON (can be dict/list or a JSON string)"
                }),
                "path": ("STRING", {
                    "default": "",
                    "tooltip": "Dot-separated path into the JSON (e.g. 'a.b.0.c'). Empty returns whole JSON."
                })
            }
        }

    TITLE = "JSON Selector"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("json", "error")
    FUNCTION = "execute"
    CATEGORY = "unset"
    DESCRIPTION = "Select a single item inside a JSON input using a dot path and return a pretty-printed JSON string."

    def _parse_input(self, data):
        # If it's a string, try to parse as JSON; otherwise assume it's already a structure
        if isinstance(data, (bytes, bytearray)):
            try:
                data = data.decode('utf-8')
            except Exception:
                pass
        if isinstance(data, str):
            s = data.strip()
            if s == "":
                return None
            try:
                return _json.loads(s)
            except Exception:
                # Not valid JSON string; return as raw string
                return data

        return data

    def execute(self, json, path: str):
        try:
            obj = self._parse_input(json)

            if path is None:
                path = ""

            if path.strip() == "":
                # Return whole object pretty-printed
                try:
                    pretty = _json.dumps(obj, indent=2, ensure_ascii=False)
                except Exception:
                    pretty = str(obj)
                return (pretty, None)

            # Walk the path
            cur = obj
            for segment in [p for p in path.split('.') if p != '']:
                if cur is None:
                    raise KeyError(f"Path segment '{segment}' not found (None encountered)")

                # Try integer index for lists
                try:
                    idx = int(segment)
                    if isinstance(cur, (list, tuple)):
                        cur = cur[idx]
                        continue
                    else:
                        # segment looked like an index but current is not a list
                        raise KeyError(f"Segment '{segment}' is an index but current item is not a list")
                except ValueError:
                    # not an integer index — treat as dict key
                    pass

                if isinstance(cur, dict):
                    if segment in cur:
                        cur = cur[segment]
                    else:
                        raise KeyError(f"Key '{segment}' not found in object")
                else:
                    # Cannot index into this type by key
                    raise KeyError(f"Cannot access key '{segment}' on type {type(cur).__name__}")

            # Format selected item
            try:
                pretty = _json.dumps(cur, indent=2, ensure_ascii=False)
            except Exception:
                pretty = str(cur)

            return (pretty, None)

        except Exception as e:
            return (None, str(e))

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        import random
        return random.randint(0, 32768)
