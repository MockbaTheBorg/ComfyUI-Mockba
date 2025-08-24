"""
mbChronoOut - passthrough node that calculates elapsed time since a provided timestamp.

Inputs:
 - input: any type, passed through to output
 - time: INT timestamp as produced by `mbChronoIn` (perf_counter_ns)

Outputs:
 - out: the input passed through (any type)
 - elapsed: elapsed time in seconds (FLOAT) with high precision

If the provided `time` is None or invalid the node returns elapsed as 0.0.
"""
import time as _time

from .common import any_typ, CATEGORIES


class mbChronoOut:
    """Calculate elapsed time from a previously captured perf_counter_ns timestamp."""

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input": (any_typ, {
                    "tooltip": "Any value to pass through"
                }),
                "time": ("INT", {
                    "forceInput": True,
                    "tooltip": "Timestamp produced by mbChronoIn (perf_counter_ns)"
                }),
            }
        }

    TITLE = "Chrono Out"
    RETURN_TYPES = (any_typ, "FLOAT")
    RETURN_NAMES = ("out", "elapsed")
    FUNCTION = "chrono_out"
    CATEGORY = "unset"
    DESCRIPTION = "Pass input through and output elapsed time in seconds since provided timestamp."
    OUTPUT_NODE = True  # Marks this node as an output node in the UI

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Force execution so elapsed is recalculated each run
        return _time.perf_counter_ns()

    def chrono_out(self, input, time: int):
        """Return the input and elapsed seconds since `time` (perf_counter_ns).

        Args:
            input: any value to pass through
            time: integer nanosecond timestamp from perf_counter_ns

        Returns:
            tuple: (input, elapsed_seconds)
        """
        try:
            if time is None:
                return (input, 0.0)

            now = _time.perf_counter_ns()
            # time may be a string if wired incorrectly; try to coerce
            start_ns = int(time)
            elapsed_ns = now - start_ns
            elapsed_s = elapsed_ns / 1e9
            return (input, float(elapsed_s))
        except Exception:
            # On error, return zero elapsed but pass through the input
            return (input, 0.0)
