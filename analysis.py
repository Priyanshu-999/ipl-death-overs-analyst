"""Analyse IPL death-overs bowling from Cricsheet ball-by-ball data.

Question: which bowlers actually win matches in the death overs?

Definitions (decided once, used everywhere, including queries.sql):
- Death overs = overs 16-20 of a regulation innings (innings 1 or 2 only,
  so super overs are excluded). The raw `ball` column reads 0.1 for the
  first ball of over 1, so over_number = int(ball) + 1.
- A legal ball has no wide and no no-ball on it.
- Runs conceded by the bowler = runs_off_bat + wides + noballs.
  Byes and legbyes are NOT charged to the bowler.
- A bowler wicket is any dismissal except a run out.
- A dot ball is a legal ball with no run off the bat and no bye/legbye.
- Economy = runs conceded / (legal balls / 6).
- A bowler only qualifies for the rankings with at least 100 legal
  death-over balls, so a bowler with one good over cannot top the list.

Run from the project root (after fetch_data.py):
    python analysis.py

Outputs:
    data/death_bowler_stats.csv   per-bowler death-over numbers
    data/ipl.db                   SQLite database (deliveries + stats)
    charts/*.png                  the three charts
"""

import os
import sqlite3

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHART_DIR = os.path.join(BASE_DIR, "charts")
DELIVERIES_PATH = os.path.join(DATA_DIR, "deliveries.csv")
STATS_PATH = os.path.join(DATA_DIR, "death_bowler_stats.csv")
DB_PATH = os.path.join(DATA_DIR, "ipl.db")
MIN_LEGAL_BALLS = 100


def clean_data(df):
    """Add the derived columns every later step relies on.

    Returns a new DataFrame with: over_number, is_death, is_legal,
    bowler_runs, is_bowler_wicket and is_dot.
    """
    df = df.copy()
    # Season labels mix plain years (2017) and spans ("2020/21"),
    # so keep them as text.
    df["season"] = df["season"].astype(str)
    # A ball is legal only when it is neither a wide nor a no-ball.
    # This must be computed BEFORE missing values are filled with 0.
    df["is_legal"] = df["wides"].isna() & df["noballs"].isna()
    for col in ["runs_off_bat", "wides", "noballs", "byes", "legbyes"]:
        df[col] = df[col].fillna(0)
    df["over_number"] = df["ball"].astype(int) + 1
    df["is_death"] = (df["over_number"] >= 16) & (df["over_number"] <= 20) & (df["innings"] <= 2)
    df["bowler_runs"] = df["runs_off_bat"] + df["wides"] + df["noballs"]
    df["is_bowler_wicket"] = df["wicket_type"].notna() & (df["wicket_type"] != "run out")
    df["is_dot"] = df["is_legal"] & (df["runs_off_bat"] == 0) & (df["byes"] == 0) & (df["legbyes"] == 0)
    return df


def bowler_death_stats(death):
    """Aggregate death-over numbers per bowler, one row per bowler."""
    stats = (
        death.groupby("bowler")
        .agg(
            matches=("match_id", "nunique"),
            deliveries=("ball", "count"),
            legal_balls=("is_legal", "sum"),
            runs_conceded=("bowler_runs", "sum"),
            wickets=("is_bowler_wicket", "sum"),
            dot_balls=("is_dot", "sum"),
        )
        .reset_index()
    )
    stats["economy"] = stats["runs_conceded"] / (stats["legal_balls"] / 6)
    stats["dot_ball_pct"] = stats["dot_balls"] / stats["legal_balls"] * 100
    stats["qualified"] = stats["legal_balls"] >= MIN_LEGAL_BALLS
    return stats.sort_values("economy")


def save_charts(qualified):
    """Save the three charts used in the README."""
    os.makedirs(CHART_DIR, exist_ok=True)

    # 1. Lowest death-over economy, top 15 qualified bowlers.
    top_eco = qualified.nsmallest(15, "economy").iloc[::-1]
    plt.figure(figsize=(10, 7))
    plt.barh(top_eco["bowler"], top_eco["economy"])
    plt.xlabel("Death-over economy (runs per over)")
    plt.title("Lowest death-over economy (min. 100 legal death balls)")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "death_economy_top15.png"), dpi=150)
    plt.close()

    # 2. Wickets vs economy: the trade-off between taking wickets and
    # keeping runs down. Annotate the five highest wicket-takers.
    plt.figure(figsize=(10, 7))
    plt.scatter(qualified["economy"], qualified["wickets"], alpha=0.7)
    plt.xlabel("Death-over economy (runs per over)")
    plt.ylabel("Death-over wickets")
    plt.title("Death-over wickets vs economy (qualified bowlers)")
    for _, row in qualified.nlargest(5, "wickets").iterrows():
        plt.annotate(row["bowler"], (row["economy"], row["wickets"]))
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "wickets_vs_economy.png"), dpi=150)
    plt.close()

    # 3. Highest dot-ball percentage, top 15 qualified bowlers.
    top_dots = qualified.nlargest(15, "dot_ball_pct").iloc[::-1]
    plt.figure(figsize=(10, 7))
    plt.barh(top_dots["bowler"], top_dots["dot_ball_pct"])
    plt.xlabel("Dot balls (% of legal death balls)")
    plt.title("Highest death-over dot-ball % (min. 100 legal death balls)")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "dot_ball_top15.png"), dpi=150)
    plt.close()
    print(f"Charts saved to {CHART_DIR}")


def save_database(df, stats):
    """Store the cleaned deliveries and the bowler stats in SQLite."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("deliveries", conn, index=False)
    stats.to_sql("death_bowler_stats", conn, index=False)
    conn.close()
    print(f"SQLite database saved to {DB_PATH}")


def main():
    df = pd.read_csv(DELIVERIES_PATH, dtype={"season": str}, low_memory=False)
    df = clean_data(df)
    death = df[df["is_death"]]
    print(f"Total deliveries: {len(df):,} across {df['match_id'].nunique():,} matches")
    print(f"Death-over deliveries (overs 16-20, innings 1-2): {len(death):,}")
    stats = bowler_death_stats(death)
    stats.to_csv(STATS_PATH, index=False)
    qualified = stats[stats["qualified"]]
    print(f"Bowlers with >= {MIN_LEGAL_BALLS} legal death balls: {len(qualified)}")
    print("\nTop 10 by economy (qualified):")
    print(qualified.nsmallest(10, "economy")[["bowler", "matches", "legal_balls", "runs_conceded", "wickets", "economy"]].to_string(index=False))
    print("\nTop 10 by wickets (qualified):")
    print(qualified.nlargest(10, "wickets")[["bowler", "matches", "legal_balls", "runs_conceded", "wickets", "economy"]].to_string(index=False))
    print("\nTop 10 by dot-ball % (qualified):")
    print(qualified.nlargest(10, "dot_ball_pct")[["bowler", "matches", "legal_balls", "dot_balls", "dot_ball_pct", "economy"]].to_string(index=False))
    save_charts(qualified)
    save_database(df, stats)


if __name__ == "__main__":
    main()
