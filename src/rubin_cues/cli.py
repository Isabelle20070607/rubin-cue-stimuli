from __future__ import annotations

import argparse
import json
from typing import Any

from .bank import generate_bank
from .combinations import write_combination_audit
from .config import load_config
from .montage import create_montages
from .prototype import write_dimension_proof, write_face_outline_proof
from .schedule import make_continuous_schedule, make_short_schedule, write_schedule
from .summarize import summarize_continuous, summarize_short
from .validate import validate_manifest


def _json_result(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rubin-cues",
        description="Generate and operate the deterministic Rubin cue stimulus bank.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("generate", help="render a stimulus bank")
    generate.add_argument("--config", required=True)
    generate.add_argument("--output")
    generate.add_argument("--overwrite", action="store_true")

    prototype = commands.add_parser("prototype", help="render five isolated cue-dimension proofs")
    prototype.add_argument("--config", default="configs/v1.toml")
    prototype.add_argument("--output", default="tmp/prototype")

    outline_proof = commands.add_parser(
        "outline-proof", help="render the face-outline endpoint for compatible source contours"
    )
    outline_proof.add_argument("--config", default="configs/v1.toml")
    outline_proof.add_argument("--output", default="tmp/outline-face-proof")
    outline_proof.add_argument(
        "--source",
        action="append",
        dest="source_ids",
        help="source ID to render; repeat to compare selected registered candidates",
    )

    combinations = commands.add_parser(
        "combinations", help="write the pre-render factorial combination audit"
    )
    combinations.add_argument("--output", default="tmp/combination-audit")
    combinations.add_argument("--config", default="configs/v1.toml")

    validate = commands.add_parser("validate", help="validate a frozen bank")
    validate.add_argument("--manifest", required=True)

    montage = commands.add_parser("montage", help="create visual QC grids")
    montage.add_argument("--manifest", required=True)
    montage.add_argument("--output")
    montage.add_argument("--cell-size", type=int, default=160)

    schedule = commands.add_parser("schedule", help="write a randomized trial schedule")
    schedule.add_argument("--mode", choices=("short", "continuous"), required=True)
    schedule.add_argument("--config", default="configs/v1.toml")
    schedule.add_argument("--manifest", required=True)
    schedule.add_argument("--participant", required=True)
    schedule.add_argument("--selection")
    schedule.add_argument("--output", required=True)
    schedule.add_argument("--seed", type=int)

    summarize = commands.add_parser("summarize", help="summarize experiment responses")
    summarize.add_argument("--responses", required=True)
    summarize.add_argument("--mode", choices=("short", "continuous"), required=True)
    summarize.add_argument("--config", default="configs/v1.toml")
    summarize.add_argument("--manifest")
    summarize.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "generate":
        result = generate_bank(load_config(args.config), args.output, args.overwrite)
    elif args.command == "prototype":
        result = write_dimension_proof(load_config(args.config), args.output)
    elif args.command == "outline-proof":
        result = write_face_outline_proof(
            load_config(args.config), args.output, source_ids=args.source_ids
        )
    elif args.command == "combinations":
        result = write_combination_audit(
            args.output, design_profile=load_config(args.config).design_profile
        )
    elif args.command == "validate":
        result = validate_manifest(args.manifest)
    elif args.command == "montage":
        result = create_montages(args.manifest, args.output, args.cell_size)
    elif args.command == "schedule":
        config = load_config(args.config)
        if args.mode == "short":
            rows = make_short_schedule(config, args.manifest, args.participant, seed=args.seed)
        else:
            if not args.selection:
                raise SystemExit("continuous schedules require --selection")
            rows = make_continuous_schedule(
                config,
                args.manifest,
                args.selection,
                args.participant,
                seed=args.seed,
            )
        output = write_schedule(rows, args.output)
        result = {
            "ok": True,
            "mode": args.mode,
            "trial_count": len(rows),
            "output": str(output),
        }
    elif args.command == "summarize":
        if args.mode == "short":
            if not args.manifest:
                raise SystemExit("short summaries require --manifest")
            result = summarize_short(
                load_config(args.config), args.responses, args.manifest, args.output
            )
        else:
            result = summarize_continuous(args.responses, args.output)
    else:  # pragma: no cover - argparse guarantees a known command
        raise AssertionError(args.command)

    _json_result(result)
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
