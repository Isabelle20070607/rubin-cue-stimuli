from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from common import append_row, frames, prepare_display, read_schedule, response_for_key

FIELDS = [
    "participant",
    "mode",
    "block",
    "trial",
    "stimulus_id",
    "response",
    "response_key",
    "response_time_ms",
    "fixation_ms_requested",
    "fixation_frames",
    "stimulus_ms_requested",
    "stimulus_frames",
    "mask_ms_requested",
    "mask_frames",
    "refresh_hz_measured",
    "dropped_frames_total",
    "fixation_during_stimulus",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the short first-interpretation task.")
    parser.add_argument("--schedule", required=True)
    parser.add_argument("--display", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--production", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    display = prepare_display(args.display, args.production)
    schedule = read_schedule(args.schedule)
    if not schedule or any(row["mode"] != "short" for row in schedule):
        raise ValueError("schedule contains no short-task trials or mixes modes")

    from psychopy import core, event, monitors, visual

    monitor = monitors.Monitor(str(display["monitor_name"]))
    if float(display.get("width_cm", 0)) > 0:
        monitor.setWidth(float(display["width_cm"]))
        monitor.setDistance(float(display["distance_cm"]))
        monitor.setSizePix(
            (int(display["resolution_width_px"]), int(display["resolution_height_px"]))
        )
    window = visual.Window(
        size=(int(display["resolution_width_px"]), int(display["resolution_height_px"])),
        monitor=monitor,
        fullscr=bool(display.get("fullscreen", False)),
        units="deg",
        color=0.0,
        colorSpace="rgb",
        allowGUI=not args.production,
        waitBlanking=True,
    )
    window.recordFrameIntervals = True
    measured = window.getActualFrameRate(nIdentical=20, nMaxFrames=240, nWarmUpFrames=30)
    refresh_hz = float(measured or display["refresh_hz"])
    fixation = visual.TextStim(window, text="+", height=0.45, color="white", units="deg")
    prompt = visual.TextStim(
        window,
        text="报告首次知觉：face / vase / unsure",
        height=0.55,
        color="white",
        units="deg",
    )
    response_clock = core.Clock()
    try:
        for row in schedule:
            fixation_count = frames(row["fixation_ms"], refresh_hz)
            stimulus_count = frames(row["stimulus_ms"], refresh_hz)
            mask_count = frames(row["mask_ms"], refresh_hz)
            stimulus = visual.ImageStim(
                window,
                image=row["stimulus_path"],
                size=(
                    float(row["visual_angle_width_deg"]),
                    float(row["visual_angle_height_deg"]),
                ),
                units="deg",
                interpolate=True,
            )
            mask = visual.ImageStim(
                window,
                image=row["mask_path"],
                size=(
                    float(row["visual_angle_width_deg"]),
                    float(row["visual_angle_height_deg"]),
                ),
                units="deg",
                interpolate=True,
            )
            for _ in range(fixation_count):
                fixation.draw()
                window.flip()
            for _ in range(stimulus_count):
                stimulus.draw()
                if bool(display.get("fixation_during_stimulus", False)):
                    fixation.draw()
                window.flip()
            for _ in range(mask_count):
                mask.draw()
                window.flip()
            event.clearEvents(eventType="keyboard")
            response_clock.reset()
            response = None
            response_key = ""
            while response is None:
                prompt.draw()
                window.flip()
                keys = event.getKeys(
                    keyList=[row["face_key"], row["vase_key"], row["unsure_key"], "escape"]
                )
                if "escape" in keys:
                    raise KeyboardInterrupt
                if keys:
                    response_key = keys[-1]
                    response = response_for_key(row, response_key)
            append_row(
                args.output,
                {
                    **row,
                    "response": response,
                    "response_key": response_key,
                    "response_time_ms": round(response_clock.getTime() * 1000, 3),
                    "fixation_ms_requested": row["fixation_ms"],
                    "fixation_frames": fixation_count,
                    "stimulus_ms_requested": row["stimulus_ms"],
                    "stimulus_frames": stimulus_count,
                    "mask_ms_requested": row["mask_ms"],
                    "mask_frames": mask_count,
                    "refresh_hz_measured": round(refresh_hz, 4),
                    "dropped_frames_total": int(window.nDroppedFrames),
                    "fixation_during_stimulus": bool(
                        display.get("fixation_during_stimulus", False)
                    ),
                },
                FIELDS,
            )
    except KeyboardInterrupt:
        return 130
    finally:
        window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
