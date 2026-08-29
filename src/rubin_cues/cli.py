from __future__ import annotations

import argparse
import json
from typing import Any

from .bank import generate_bank
from .config import load_config


def _json_result(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rubin-cues",
        description="Generate the Rubin cue stimulus images.",
    )
    parser.add_argument("--config", default="config.toml")
    parser.add_argument("--output")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = generate_bank(load_config(args.config), args.output, args.overwrite)
    _json_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
