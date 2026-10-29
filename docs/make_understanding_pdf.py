"""Build docs/UNDERSTANDING.pdf: a plain-language guide to this project.

Run from the project root:
    python docs/make_understanding_pdf.py

Uses fpdf2 (pip install fpdf2). The text is kept ASCII-only so the
built-in Helvetica font renders every character.
"""

import os

from fpdf import FPDF

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(BASE_DIR, "docs", "UNDERSTANDING.pdf")

SECTIONS = [
    (
        "1. The problem, in plain words",
        "In a T20 cricket match, the last five overs (overs 16 to 20) are "
        "called the death overs. Batters attack hard, so runs flow fast, "
        "but a bowler who takes wickets or bowls dot balls here can still "
        "win the match. This project asks one sharp question: which bowlers "
        "actually perform best in the death overs? It answers with numbers, "
        "not reputation, using every ball bowled in the IPL data we "
        "downloaded.",
    ),
    (
        "2. The dataset",
        "Source: Cricsheet, https://cricsheet.org/downloads/ipl_csv2.zip - "
        "public data, no login needed. One row is one ball bowled. After "
        "combining all matches we had 295,732 deliveries from 1,243 "
        "matches, with season labels from 2007/08 to 2026. Of those, "
        "67,173 deliveries were death-over deliveries in regulation "
        "innings. Each row tells us the match, season, innings, ball "
        "number, batting and bowling team, striker, bowler, runs off the "
        "bat, wides, no-balls, byes, legbyes, and the type of dismissal "
        "if a wicket fell.",
    ),
    (
        "3. The workflow, step by step",
        "Step 1: fetch_data.py downloads the Cricsheet zip and stacks all "
        "per-match CSV files into data/deliveries.csv. Step 2: analysis.py "
        "cleans the data (see section 5) and keeps only death overs. "
        "Step 3: it groups the death overs by bowler and computes "
        "matches, legal balls, runs conceded, wickets, dot balls, "
        "economy and dot-ball percentage. Step 4: it keeps only bowlers "
        "with at least 100 legal death balls, so tiny samples cannot top "
        "the lists. Step 5: it draws three charts and saves everything to "
        "a SQLite database, so the same rankings can be checked in SQL "
        "with queries.sql.",
    ),
    (
        "4. Definitions you must know",
        "Death overs: overs 16 to 20 of innings 1 or 2 only. Super overs "
        "(innings 3 and above) are excluded. The raw ball column reads "
        "0.1 for the first ball of over 1, so over number = int(ball) + "
        "1. Legal ball: no wide and no no-ball. Runs conceded by the "
        "bowler: runs off the bat + wides + no-balls. Byes and legbyes "
        "are NOT charged to the bowler, because the bowler did not cause "
        "them. Bowler wicket: any dismissal except a run out, because a "
        "run out is the fielders' work. Dot ball: a legal ball with no "
        "run off the bat and no bye or legbye. Economy: runs conceded "
        "divided by legal balls, multiplied by 6, i.e. runs per over.",
    ),
    (
        "5. Every main function: what it does, why, and what it outputs",
        "fetch_data.py - download_zip(url, dest): downloads the zip, or "
        "reuses it if it is already on disk. Why: re-running the project "
        "should not re-download 7 MB every time. Output: the zip file "
        "path. fetch_data.py - combine_matches(raw_dir, output): reads "
        "every per-match CSV except the *_info.csv metadata files and "
        "stacks them into one CSV. Why: 1,243 small files are impossible "
        "to analyse one by one. Output: data/deliveries.csv plus a "
        "printed count of matches, rows and seasons. analysis.py - "
        "clean_data(df): adds over_number, is_death, is_legal, "
        "bowler_runs, is_bowler_wicket and is_dot. Why: every later "
        "calculation depends on these six columns being defined exactly "
        "once, so Python and SQL can never disagree. Output: a cleaned "
        "DataFrame. analysis.py - bowler_death_stats(death): groups death "
        "overs by bowler and computes matches, deliveries, legal balls, "
        "runs, wickets, dots, economy and dot-ball percentage, then "
        "flags bowlers with 100+ legal balls as qualified. Why: one "
        "groupby replaces dozens of manual loops. Output: a ranked "
        "DataFrame and data/death_bowler_stats.csv. analysis.py - "
        "save_charts(qualified): draws the economy top 15, the wickets "
        "vs economy scatter, and the dot-ball top 15. Why: a chart shows "
        "the trade-off between wickets and economy faster than a table. "
        "Output: three PNG files in charts/. analysis.py - "
        "save_database(df, stats): writes the cleaned deliveries and the "
        "bowler stats into data/ipl.db. Why: SQL practice on the same "
        "data, and proof the Python numbers match the SQL numbers. "
        "Output: the SQLite database file.",
    ),
    (
        "6. Key findings (from the real data)",
        "156 bowlers bowled at least 100 legal death balls. Best economy: "
        "Sohail Tanvir at 6.82 runs per over, but on only 103 balls in 10 "
        "matches, so treat that with caution. The high-volume economy "
        "leader is SP Narine at 7.25 over 1,105 balls in 142 matches. "
        "Most death wickets: Bhuvneshwar Kumar with 119, then DJ Bravo "
        "with 115, then SL Malinga with 108 at an economy of only 7.86. "
        "Best dot-ball percentage: Noor Ahmad at 40.4 percent (151 "
        "balls), then Narine at 37.4 percent over 1,105 balls. The honest "
        "answer to the project question: nobody dominates both lists. "
        "Malinga and Narine are the two bowlers who are elite on wickets "
        "AND economy, which is why they are the names to defend in an "
        "interview.",
    ),
    (
        "7. How to explain this project in an interview (60 seconds)",
        "Say this: 'I wanted to find which bowlers actually perform in "
        "the IPL death overs, so I downloaded ball-by-ball data from "
        "Cricsheet - about 296 thousand deliveries from 1,243 matches. "
        "I defined death overs as 16 to 20, counted only legal balls, "
        "charged the bowler only for runs off the bat plus wides and "
        "no-balls, and required 100 legal death balls before ranking "
        "anyone. Then I ranked bowlers by economy, wickets and dot-ball "
        "percentage in both Python and SQL, and the two matched. The "
        "finding was that wicket-takers usually leak runs, and only "
        "Malinga and Narine were elite on both lists.' Then stop and let "
        "them ask questions.",
    ),
    (
        "8. Five likely interview questions and answers",
        "Q1. Why did you choose overs 16 to 20 as death overs? A: That is "
        "the standard last-five-overs phase in a 20-over match, when "
        "batters attack hardest and bowling under pressure matters most. "
        "Q2. Why the 100-ball minimum? A: Without it, a bowler with one "
        "good over would top the economy list. Sohail Tanvir leads at "
        "6.82 but on only 103 balls, while Narine holds 7.25 over 1,105 "
        "balls, which is far more trustworthy. Q3. Why do you exclude "
        "byes and legbyes from the bowler's runs? A: Those runs are not "
        "the bowler's fault - the ball beat the batter and the keeper. "
        "Charging them to the bowler would punish good balls. Q4. Why do "
        "you exclude run outs from bowler wickets? A: A run out is "
        "created by the fielders, not by the delivery, so counting it "
        "would credit the bowler for someone else's work. Q5. Why do "
        "the top wicket-takers have worse economies? A: Attacking "
        "bowling takes wickets but also concedes boundaries, so there is "
        "a trade-off, which the wickets-vs-economy chart shows clearly. "
        "Malinga and Narine are special because they beat that trade-off.",
    ),
]


def build_pdf():
    """Write the guide PDF, one section per page flow."""
    pdf = FPDF()

    def mc(w, h, txt):
        pdf.multi_cell(w, h, txt, new_x="LMARGIN", new_y="NEXT")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    mc(0, 12, "IPL Death-Overs Analyst")
    pdf.set_font("Helvetica", "", 13)
    mc(0, 8, "Understanding guide: the whole project in simple language")
    pdf.ln(4)
    for heading, body in SECTIONS:
        pdf.set_font("Helvetica", "B", 14)
        mc(0, 9, heading)
        pdf.set_font("Helvetica", "", 11)
        mc(0, 6, body)
        pdf.ln(3)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    pdf.output(OUT_PATH)
    print(f"PDF saved to {OUT_PATH}")


if __name__ == "__main__":
    build_pdf()
