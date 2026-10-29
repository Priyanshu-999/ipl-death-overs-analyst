# IPL Death-Overs Analyst

**Question: which bowlers actually win matches in the death overs?**

A beginner data-analysis project: real ball-by-ball IPL data, cleaned in
Python, queried in SQL, and turned into charts and a clear answer.

## Dataset

- **Source:** Cricsheet (public, no login needed) —
  <https://cricsheet.org/downloads/ipl_csv2.zip>
- **What was actually downloaded and processed:**
  - 1,243 matches (one CSV file per match)
  - 295,732 deliveries (one row per ball bowled)
  - Season labels from 2007/08 to 2026 (19 labels, exactly as labelled
    in the data)
  - 67,173 death-over deliveries (overs 16-20, innings 1-2)
- The raw download is **not** committed to git (see `.gitignore`).
  Run `fetch_data.py` and it downloads and rebuilds everything.

## How to run

```bash
pip install -r requirements.txt
python fetch_data.py   # downloads Cricsheet data, builds data/deliveries.csv
python analysis.py     # cleans, ranks, charts, builds data/ipl.db
sqlite3 data/ipl.db < queries.sql   # the same rankings, in SQL
```

## Definitions (used identically in Python and SQL)

- **Death overs** = overs 16-20 of a regulation innings (innings 1 or 2
  only, so super overs are excluded). The raw `ball` column reads `0.1`
  for the first ball of over 1, so over number = int(ball) + 1.
- **Legal ball** = no wide and no no-ball on it.
- **Runs conceded by the bowler** = runs off the bat + wides + no-balls.
  Byes and legbyes are *not* charged to the bowler.
- **Bowler wicket** = any dismissal except a run out.
- **Dot ball** = a legal ball with no run off the bat and no bye/legbye.
- **Economy** = runs conceded / (legal balls / 6).
- **Qualifying threshold** = at least 100 legal death-over balls.
  Without it, a bowler with one good over would top the list.
  156 bowlers qualify.

## Key findings (all from the data above)

1. **Best death-over economy:** Sohail Tanvir at 6.82 runs per over —
   but on only 103 legal balls in 10 matches, just over the threshold.
   The high-volume economy king is **SP Narine at 7.25** over 1,105
   legal balls in 142 matches.
2. **Most death-over wickets:** Bhuvneshwar Kumar with **119** (1,605
   balls, 169 matches, economy 9.30), then DJ Bravo with 115, then
   **SL Malinga with 108 at an economy of only 7.86**.
3. **The rare double:** Malinga and Narine are the only bowlers who are
   elite on *both* lists — lots of wickets *and* a low economy.
   JJ Bumrah is the modern version of the same profile: 102 wickets
   at 8.19.
4. **Best dot-ball percentage:** Noor Ahmad at 40.4% of legal death
   balls (151 balls, 22 matches); Narine again at 37.4% over 1,105 balls.
5. **The answer to the question:** nobody dominates both lists, and
   that *is* the insight. Wicket-takers like Bhuvneshwar and Bravo leak
   9.3+ runs per over, because attacking bowling costs runs. If you
   must pick one death bowler from this data, pick Malinga
   (108 wickets, 7.86 economy) or Narine (84 wickets, 7.25 economy) —
   they are the two names the numbers support on both counts.
6. **Caveat, stated honestly:** economy leaders on small samples
   (Tanvir, 103 balls) are not comparable to bowlers with 1,000+
   balls. That is why every table shows matches and balls alongside
   the headline number.

## Charts

- `charts/death_economy_top15.png` — lowest death-over economy
- `charts/wickets_vs_economy.png` — the wickets-vs-economy trade-off
- `charts/dot_ball_top15.png` — highest dot-ball percentage

## Files

| File | What it is |
| --- | --- |
| `fetch_data.py` | Downloads the Cricsheet zip and combines all matches into `data/deliveries.csv` |
| `analysis.py` | Cleaning, bowler rankings, charts, SQLite database |
| `queries.sql` | 5 SQL queries reproducing the rankings |
| `charts/` | The 3 charts (PNG) |
| `docs/UNDERSTANDING.pdf` | Plain-language guide: every function, interview script, Q&A |
| `docs/make_understanding_pdf.py` | Script that builds the PDF |

## Skills this project shows

Python (pandas), SQL (SQLite), matplotlib charts, data cleaning
(missing values, wides/no-balls, super-over filtering), reproducible
pipelines (fetch -> clean -> analyse -> chart), and honest reporting
of sample sizes and caveats.

## Pushing this repo to your own GitHub (run these yourself)

```bash
git remote add origin <your-repo-url>
git push -u origin main
```

Replace `<your-repo-url>` with the URL of the empty repo you create
on GitHub. The data folder is ignored by git on purpose; anyone who
clones the repo re-downloads the data with `python fetch_data.py`.
