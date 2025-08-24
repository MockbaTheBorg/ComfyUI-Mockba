"""
mbChronoIn - passthrough node that emits a high-resolution timestamp.

Outputs:
 - out: the input passed through (any type)
 - time: high-resolution timestamp in nanoseconds (INT)

This node is intended to be paired with `mbChronoOut` placed later in a graph
to measure elapsed execution time between two points.
"""
import time

from .common import any_typ, CATEGORIES


class mbChronoIn:
    """Pass the input through and emit a high-resolution timestamp (ns)."""

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input": (any_typ, {
                    "tooltip": "Any value to pass through"
                }),
            }
        }

    TITLE = "Chrono In"
    RETURN_TYPES = (any_typ, "INT")
    RETURN_NAMES = ("out", "time")
    FUNCTION = "chrono_in"
    CATEGORY = "unset"
    DESCRIPTION = "Pass input through and output a high-resolution timestamp (nanoseconds)."

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Force execution so timestamps are always fresh
        return time.perf_counter_ns()

    def chrono_in(self, input):
        """Return the original input and the current perf_counter_ns timestamp."""
        ts = time.perf_counter_ns()
        return (input, ts)
