#!/usr/bin/env python3
"""Run the mbHashGenerator ComfyUI node from the command line."""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent
NODE_FILE = REPO_ROOT / "modules" / "mbHashGenerator.py"
NODE_CLASS_NAME = "mbHashGenerator"


def load_node_class() -> type:
    """Load the node class directly from its module file."""
    spec = importlib.util.spec_from_file_location("mockba_mbHashGenerator", NODE_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load node module from {NODE_FILE}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    try:
        return getattr(module, NODE_CLASS_NAME)
    except AttributeError as exc:
        raise RuntimeError(f"Node class {NODE_CLASS_NAME} not found in {NODE_FILE}") from exc


def parse_bool(value: str) -> bool:
    """Convert a command-line boolean string into a Python bool."""
    normalized = value.strip().lower()
    if normalized in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "f", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(
        f"Invalid boolean value: {value!r}. Use true/false, yes/no, on/off, or 1/0."
    )


def get_input_spec_parts(input_spec: Any) -> tuple[Any, dict[str, Any]]:
    """Normalize a ComfyUI INPUT_TYPES entry into type info and metadata."""
    if not isinstance(input_spec, tuple) or not input_spec:
        raise ValueError(f"Unsupported input spec: {input_spec!r}")

    type_info = input_spec[0]
    metadata = input_spec[1] if len(input_spec) > 1 and isinstance(input_spec[1], dict) else {}
    return type_info, metadata


def build_parser(node_cls: type) -> tuple[argparse.ArgumentParser, list[str]]:
    """Build an argparse parser from the node INPUT_TYPES definition."""
    parser = argparse.ArgumentParser(
        description=getattr(node_cls, "DESCRIPTION", None) or getattr(node_cls, "TITLE", node_cls.__name__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit compact JSON instead of pretty-printed JSON.",
    )

    input_names: list[str] = []
    input_types = node_cls.INPUT_TYPES()

    for section_name in ("required", "optional"):
        section_inputs = input_types.get(section_name, {})
        if not section_inputs:
            continue

        group = parser.add_argument_group(f"{section_name} inputs")

        for input_name, input_spec in section_inputs.items():
            type_info, metadata = get_input_spec_parts(input_spec)
            default = metadata.get("default")
            help_text = metadata.get("tooltip", "")
            argument_name = f"--{input_name}"
            argument_kwargs: dict[str, Any] = {"help": help_text, "dest": input_name}

            if isinstance(type_info, (list, tuple)) and not isinstance(type_info, str):
                choices = list(type_info)
                argument_kwargs["choices"] = choices
                if default is not None:
                    argument_kwargs["default"] = default
                elif section_name == "required":
                    argument_kwargs["required"] = True
            elif type_info == "BOOLEAN":
                argument_kwargs["type"] = parse_bool
                argument_kwargs["metavar"] = "BOOL"
                if default is not None:
                    argument_kwargs["default"] = default
                elif section_name == "required":
                    argument_kwargs["required"] = True
            elif type_info == "INT":
                argument_kwargs["type"] = int
                if default is not None:
                    argument_kwargs["default"] = default
                elif section_name == "required":
                    argument_kwargs["required"] = True
            elif type_info == "FLOAT":
                argument_kwargs["type"] = float
                if default is not None:
                    argument_kwargs["default"] = default
                elif section_name == "required":
                    argument_kwargs["required"] = True
            else:
                argument_kwargs["type"] = str
                if default is not None:
                    argument_kwargs["default"] = default
                elif section_name == "required":
                    argument_kwargs["required"] = True

            group.add_argument(argument_name, **argument_kwargs)
            input_names.append(input_name)

    return parser, input_names


def to_jsonable(value: Any) -> Any:
    """Convert node outputs into JSON-safe values."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    return repr(value)


def map_outputs(node_cls: type, result: Any) -> dict[str, Any]:
    """Map tuple outputs onto RETURN_NAMES when available."""
    return_names = tuple(getattr(node_cls, "RETURN_NAMES", ()) or ())

    if not isinstance(result, tuple):
        result = (result,)

    if return_names and len(return_names) == len(result):
        return {name: to_jsonable(value) for name, value in zip(return_names, result)}

    return {f"output_{index}": to_jsonable(value) for index, value in enumerate(result, start=1)}


def main() -> int:
    node_cls = load_node_class()
    parser, input_names = build_parser(node_cls)
    args = parser.parse_args()

    node = node_cls()
    function_name = getattr(node_cls, "FUNCTION")
    function = getattr(node, function_name)
    node_inputs = {name: getattr(args, name) for name in input_names}

    with contextlib.redirect_stdout(sys.stderr):
        result = function(**node_inputs)

    payload = {
        "node": node_cls.__name__,
        "function": function_name,
        "inputs": to_jsonable(node_inputs),
        "outputs": map_outputs(node_cls, result),
    }

    json.dump(payload, sys.stdout, indent=None if args.compact else 2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())