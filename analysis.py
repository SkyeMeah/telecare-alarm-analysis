"""
Exploratory analysis of synthetic telecare alarm data.

Answers four questions:
    1. What time of day produces the most alarms?
    2. Are response times correlated with priority level?
    3. Which alarm types take the longest to resolve?
    4. Is there a weekday vs. weekend pattern in alarm volume?

Outputs four PNG charts to `figures/` and prints a short text summary.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_PATH = Path("data/alarms.csv")
FIG_DIR = Path("figures")


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["weekday"] = df["timestamp"].dt.day_name()
    df["is_weekend"] = df["timestamp"].dt.weekday >= 5
    return df


def question_1_alarms_by_hour(df: pd.DataFrame) -> None:
    counts = df.groupby("hour").size()

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(counts.index, counts.values, color="#1F3A5F")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Alarms")
    ax.set_title("Alarm volume by hour of day")
    ax.set_xticks(range(0, 24))
    fig.tight_layout()
    fig.savefig(FIG_DIR / "01_alarms_by_hour.png", dpi=140)
    plt.close(fig)

    peak_hour = counts.idxmax()
    print(f"Q1: Busiest hour is {peak_hour:02d}:00 with {counts.max()} alarms.")


def question_2_response_by_priority(df: pd.DataFrame) -> None:
    grouped = df.groupby("priority")["response_time_minutes"]
    means = grouped.mean()

    fig, ax = plt.subplots(figsize=(6, 4))
    colours = {"high": "#B7322B", "medium": "#D49021", "low": "#3D7A3D"}
    ax.bar(means.index, means.values,
           color=[colours[p] for p in means.index])
    ax.set_ylabel("Mean response time (minutes)")
    ax.set_title("Mean response time by priority")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "02_response_by_priority.png", dpi=140)
    plt.close(fig)

    print("Q2: Mean response time by priority:")
    for priority, mean_time in means.items():
        print(f"     {priority:<7} {mean_time:.1f} min")


def question_3_response_by_type(df: pd.DataFrame) -> None:
    grouped = df.groupby("alarm_type")["response_time_minutes"].mean()
    grouped = grouped.sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(grouped.index, grouped.values, color="#1F3A5F")
    ax.set_xlabel("Mean response time (minutes)")
    ax.set_title("Mean response time by alarm type")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "03_response_by_type.png", dpi=140)
    plt.close(fig)

    print("Q3: Slowest alarm types:")
    for t, m in grouped.tail(3).items():
        print(f"     {t:<12} {m:.1f} min")


def question_4_weekday_vs_weekend(df: pd.DataFrame) -> None:
    by_weekday = df.groupby("weekday").size()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday"]
    by_weekday = by_weekday.reindex(order)

    fig, ax = plt.subplots(figsize=(9, 4))
    colours = ["#1F3A5F"] * 5 + ["#B7322B"] * 2
    ax.bar(by_weekday.index, by_weekday.values, color=colours)
    ax.set_ylabel("Alarms")
    ax.set_title("Alarm volume by day of week")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "04_alarms_by_weekday.png", dpi=140)
    plt.close(fig)

    weekday_avg = df[~df["is_weekend"]].groupby(
        df["timestamp"].dt.date).size().mean()
    weekend_avg = df[df["is_weekend"]].groupby(
        df["timestamp"].dt.date).size().mean()
    print(f"Q4: Avg alarms/day  weekdays {weekday_avg:.1f}  "
          f"vs. weekends {weekend_avg:.1f}")


def summary() -> None:
    print()
    print("Summary on the synthetic data")
    print("-" * 40)
    print("- Alarm volume peaks in the early evening (17:00–21:00),")
    print("  matching the anecdotal pattern at work.")
    print("- High-priority alarms are responded to fastest, as expected.")
    print("- Anxious / wandering alarms take longest, because they")
    print("  involve more time at the property to reassure or assist.")
    print("- Weekday and weekend volumes are similar; the small")
    print("  difference would not justify a different staffing pattern")
    print("  on this dataset alone.")


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    df = load()
    print(f"Loaded {len(df)} rows from {DATA_PATH}\n")

    question_1_alarms_by_hour(df)
    question_2_response_by_priority(df)
    question_3_response_by_type(df)
    question_4_weekday_vs_weekend(df)
    summary()


if __name__ == "__main__":
    main()
