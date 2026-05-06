"""
Generate a synthetic dataset of telecare alarm events.

The data shape mirrors what a real telecare service might log: a timestamp,
the alarm type, the priority, the response time in minutes, the resolution
outcome, and a coarse area code. None of the data is real — there are no
real customers, addresses or call details. The distributions are tuned to
resemble what I see anecdotally at work.

Output: data/alarms.csv
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

OUT_PATH = Path("data/alarms.csv")
N_ROWS = 5000
START_DATE = datetime(2025, 6, 1)

ALARM_TYPES = {
    # type            (probability, base response mins, response variance)
    "fall":            (0.34, 7.0, 3.5),
    "wandering":       (0.10, 12.0, 6.0),
    "medication":      (0.18, 14.0, 5.0),
    "medical":         (0.14, 6.5, 3.0),
    "anxious":         (0.12, 18.0, 8.0),
    "fire":            (0.02, 4.0, 2.0),
    "false_alarm":     (0.10, 5.5, 2.5),
}

PRIORITIES = {
    "fall": "high",
    "wandering": "medium",
    "medication": "medium",
    "medical": "high",
    "anxious": "low",
    "fire": "high",
    "false_alarm": "low",
}

OUTCOMES = ["resolved_on_site", "escalated_to_999", "escalated_to_GP",
            "no_action_required", "next_day_followup"]

AREAS = ["SR1", "SR2", "SR3", "SR4", "SR5", "SR6", "NE38", "NE39"]


def hour_weight(hour: int) -> float:
    """Alarms peak in the early evening and dip overnight."""
    if 6 <= hour < 9:    return 0.9
    if 9 <= hour < 12:   return 1.0
    if 12 <= hour < 17:  return 1.2
    if 17 <= hour < 21:  return 1.6
    if 21 <= hour < 24:  return 1.1
    return 0.5  # 0–6


def sample_timestamp() -> datetime:
    """Sample a timestamp over a 90-day window, weighted by time of day."""
    while True:
        day_offset = random.randint(0, 89)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        candidate = START_DATE + timedelta(days=day_offset, hours=hour, minutes=minute)
        # Reject-sample to bias toward busier hours
        if random.random() < hour_weight(hour) / 1.6:
            return candidate


def sample_alarm_type() -> str:
    types, weights = zip(*[(k, v[0]) for k, v in ALARM_TYPES.items()])
    return random.choices(types, weights=weights, k=1)[0]


def sample_response_time(alarm_type: str, hour: int) -> float:
    base, variance = ALARM_TYPES[alarm_type][1], ALARM_TYPES[alarm_type][2]
    # Small penalty for late-night calls — fewer staff on shift.
    night_penalty = 1.4 if (hour < 6 or hour >= 22) else 1.0
    t = random.gauss(base * night_penalty, variance)
    return max(0.5, round(t, 1))


def sample_outcome(alarm_type: str) -> str:
    if alarm_type in {"fall", "medical"}:
        weights = [0.45, 0.30, 0.10, 0.10, 0.05]
    elif alarm_type == "fire":
        weights = [0.10, 0.80, 0.05, 0.05, 0.00]
    elif alarm_type == "false_alarm":
        weights = [0.05, 0.00, 0.00, 0.90, 0.05]
    else:
        weights = [0.55, 0.05, 0.15, 0.10, 0.15]
    return random.choices(OUTCOMES, weights=weights, k=1)[0]


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUT_PATH.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "area_code", "alarm_type", "priority",
            "response_time_minutes", "outcome",
        ])

        for _ in range(N_ROWS):
            ts = sample_timestamp()
            alarm_type = sample_alarm_type()
            row = [
                ts.isoformat(timespec="seconds"),
                random.choice(AREAS),
                alarm_type,
                PRIORITIES[alarm_type],
                sample_response_time(alarm_type, ts.hour),
                sample_outcome(alarm_type),
            ]
            writer.writerow(row)

    print(f"Wrote {N_ROWS} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
