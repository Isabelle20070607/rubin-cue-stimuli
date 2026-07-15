from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from common import append_row, frames, prepare_display, read_schedule, response_for_key

FIELDS = [
    "participant",
    "mode",
    "session",
    "trial",
    "stimulus_id",
    "base_id",
    "cue_axis",
    "signed_strength",
    "event_time_ms",
    "response",
    "response_key",
    "stimulus_duration_ms",
    "refresh_hz_measured",
    "dropped_frames_total",
    "fixation_during_stimulus",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the continuous stability task.")
    parser.add_argument("--schedule", required=True)
    parser.add_argument("--display", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--production", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    display = prepare_display(args.display, args.production)
    schedule = read_schedule(args.schedule)
    if not schedule or any(row["mode"] != "continuous" for row in schedule):
        raise ValueError("schedule contains no continuous-task trials or mixes modes")

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
    trial_clock = core.Clock()
    try:
        for row in schedule:
            fixation_count = frames(row["fixation_ms"], refresh_hz)
            stimulus_count = frames(row["stimulus_ms"], refresh_hz)
            iti_count = frames(row["iti_ms"], refresh_hz)
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
            for _ in range(fixation_count):
                fixation.draw()
                window.flip()
            event.clearEvents(eventType="keyboard")
            trial_clock.reset()
            last_response = None
            for _ in range(stimulus_count):
                stimulus.draw()
                if bool(display.get("fixation_during_stimulus", False)):
                    fixation.draw()
                window.flip()
                for key in event.getKeys(
                    keyList=[row["face_key"], row["vase_key"], row["unsure_key"], "escape"]
                ):
                    if key == "escape":
                        raise KeyboardInterrupt
                    response = response_for_key(row, key)
                    if response is None or response == last_response:
                        continue
                    last_response = response
                    append_row(
                        args.output,
                        {
                            **row,
                            "event_time_ms": round(trial_clock.getTime() * 1000, 3),
                            "response": response,
                            "response_key": key,
                            "stimulus_duration_ms": row["stimulus_ms"],
                            "refresh_hz_measured": round(refresh_hz, 4),
                            "dropped_frames_total": int(window.nDroppedFrames),
                            "fixation_during_stimulus": bool(
                                display.get("fixation_during_stimulus", False)
                            ),
                        },
                        FIELDS,
                    )
            for _ in range(iti_count):
                window.flip()
    except KeyboardInterrupt:
        return 130
    finally:
        window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
