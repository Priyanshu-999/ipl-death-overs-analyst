-- IPL Death-Overs Analyst: SQL queries on the deliveries table.
--
-- The deliveries table is built by analysis.py from Cricsheet data.
-- Columns used here:
--   match_id, season, innings, ball, over_number, bowling_team, bowler,
--   runs_off_bat, wides, noballs, byes, legbyes, wicket_type,
--   bowler_runs (runs_off_bat + wides + noballs),
--   is_legal (1 when no wide and no no-ball),
--   is_death (1 for overs 16-20 in innings 1-2),
--   is_bowler_wicket (1 for a dismissal that is not a run out),
--   is_dot (1 for a legal ball with no run off the bat and no bye/legbye).
--
-- Run with:  sqlite3 data/ipl.db < queries.sql
-- A bowler qualifies for the rankings with at least 100 legal
-- death-over balls, so tiny samples cannot top the lists.

-- 1. Death-over economy ranking (lowest economy first, qualified only).
SELECT
    bowler,
    COUNT(DISTINCT match_id) AS matches,
    SUM(is_legal) AS legal_balls,
    SUM(bowler_runs) AS runs_conceded,
    SUM(is_bowler_wicket) AS wickets,
    ROUND(SUM(bowler_runs) * 6.0 / SUM(is_legal), 2) AS economy
FROM deliveries
WHERE is_death = 1
GROUP BY bowler
HAVING SUM(is_legal) >= 100
ORDER BY economy ASC
LIMIT 15;

-- 2. Most death-over wickets (qualified only).
SELECT
    bowler,
    COUNT(DISTINCT match_id) AS matches,
    SUM(is_legal) AS legal_balls,
    SUM(is_bowler_wicket) AS wickets,
    ROUND(SUM(bowler_runs) * 6.0 / SUM(is_legal), 2) AS economy
FROM deliveries
WHERE is_death = 1
GROUP BY bowler
HAVING SUM(is_legal) >= 100
ORDER BY wickets DESC, economy ASC
LIMIT 15;

-- 3. Best death-over dot-ball percentage (qualified only).
SELECT
    bowler,
    SUM(is_legal) AS legal_balls,
    SUM(is_dot) AS dot_balls,
    ROUND(SUM(is_dot) * 100.0 / SUM(is_legal), 2) AS dot_ball_pct,
    ROUND(SUM(bowler_runs) * 6.0 / SUM(is_legal), 2) AS economy
FROM deliveries
WHERE is_death = 1
GROUP BY bowler
HAVING SUM(is_legal) >= 100
ORDER BY dot_ball_pct DESC
LIMIT 15;

-- 4. Most death-over matches and balls bowled (workload leaders).
SELECT
    bowler,
    COUNT(DISTINCT match_id) AS death_matches,
    SUM(is_legal) AS legal_balls,
    COUNT(*) AS deliveries,
    SUM(is_bowler_wicket) AS wickets
FROM deliveries
WHERE is_death = 1
GROUP BY bowler
ORDER BY death_matches DESC, legal_balls DESC
LIMIT 15;

-- 5. Most runs conceded in the death overs (who gets hit the hardest).
SELECT
    bowler,
    COUNT(DISTINCT match_id) AS matches,
    SUM(is_legal) AS legal_balls,
    SUM(bowler_runs) AS runs_conceded,
    ROUND(SUM(bowler_runs) * 6.0 / SUM(is_legal), 2) AS economy
FROM deliveries
WHERE is_death = 1
GROUP BY bowler
HAVING SUM(is_legal) >= 100
ORDER BY runs_conceded DESC
LIMIT 15;
