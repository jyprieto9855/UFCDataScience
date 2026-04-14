import pandas as pd
import numpy as np
import sqlite3
import warnings
warnings.filterwarnings('ignore')

# ── Build a proper SQLite database ────────────────────────────────────────
fights   = pd.read_csv('/home/claude/fights_clean.csv')
fighters = pd.read_csv('/home/claude/fighters_clean.csv')
events   = pd.read_csv('/mnt/user-data/uploads/raw_events.csv')
details  = pd.read_csv('/mnt/user-data/uploads/raw_details.csv')

conn = sqlite3.connect('/home/claude/ufc.db')
fights.to_sql('fights', conn, if_exists='replace', index=False)
fighters.to_sql('fighters', conn, if_exists='replace', index=False)
events.to_sql('events', conn, if_exists='replace', index=False)
details.to_sql('details', conn, if_exists='replace', index=False)

print("Database built. Tables:", [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])

# ── SQL Query 1: Finish rate by weight class ──────────────────────────────
q1 = conn.execute("""
    SELECT 
        Weight_Class,
        COUNT(*) AS total_fights,
        ROUND(100.0 * SUM(CASE WHEN method_cat != 'Decision' THEN 1 ELSE 0 END) / COUNT(*), 1) AS finish_rate_pct,
        ROUND(100.0 * SUM(CASE WHEN method_cat = 'KO/TKO' THEN 1 ELSE 0 END) / COUNT(*), 1) AS kotko_rate,
        ROUND(100.0 * SUM(CASE WHEN method_cat = 'Submission' THEN 1 ELSE 0 END) / COUNT(*), 1) AS sub_rate
    FROM fights
    WHERE "Win/No Contest/Draw" = 'win'
      AND Weight_Class NOT IN ('Open Weight', 'Catch Weight', '')
    GROUP BY Weight_Class
    HAVING total_fights >= 50
    ORDER BY finish_rate_pct DESC
""").fetchall()

print("\n=== Q1: Finish Rate by Weight Class ===")
print(f"{'Weight Class':<25} {'Fights':>7} {'Finish%':>8} {'KO/TKO%':>8} {'Sub%':>6}")
print("-"*58)
for row in q1:
    print(f"{row[0]:<25} {row[1]:>7} {row[2]:>7}% {row[3]:>7}% {row[4]:>5}%")

# ── SQL Query 2: Top submission types ─────────────────────────────────────
q2 = conn.execute("""
    SELECT 
        REPLACE(Method, 'SUB ', '') AS technique,
        COUNT(*) AS finishes
    FROM fights
    WHERE method_cat = 'Submission'
    GROUP BY Method
    ORDER BY finishes DESC
    LIMIT 10
""").fetchall()

print("\n=== Q2: Top Submission Techniques ===")
for row in q2:
    print(f"  {row[0]:<30} {row[1]:>4} finishes")

# ── SQL Query 3: Win rate by stance ───────────────────────────────────────
q3 = conn.execute("""
    SELECT 
        Stance,
        COUNT(*) AS fighters,
        ROUND(AVG(win_pct) * 100, 1) AS avg_win_pct,
        ROUND(AVG(total_fights), 1) AS avg_career_fights
    FROM fighters
    WHERE total_fights >= 5
      AND Stance IN ('Orthodox', 'Southpaw', 'Switch', 'Open Stance')
      AND win_pct IS NOT NULL
    GROUP BY Stance
    ORDER BY avg_win_pct DESC
""").fetchall()

print("\n=== Q3: Win Rate by Stance ===")
for row in q3:
    print(f"  {row[0]:<14} {row[1]:>5} fighters  Avg Win%: {row[2]}%  Avg Career Fights: {row[3]}")

# ── SQL Query 4: Most prolific finishers ──────────────────────────────────
q4 = conn.execute("""
    SELECT 
        f.First || ' ' || f.Last AS name,
        f.W AS wins,
        f.L AS losses,
        ROUND(f.win_pct * 100, 1) AS win_pct,
        f.total_fights
    FROM fighters f
    WHERE f.total_fights >= 15
      AND f.win_pct IS NOT NULL
    ORDER BY f.win_pct DESC, f.total_fights DESC
    LIMIT 15
""").fetchall()

print("\n=== Q4: Top Win % (min 15 fights) ===")
for row in q4:
    print(f"  {row[0]:<25} {row[1]}W-{row[2]}L  Win%: {row[3]}%  ({row[4]} fights)")

# ── SQL Query 5: Average fight time by method ─────────────────────────────
def time_to_secs(t, rnd):
    try:
        m, s = str(t).split(':')
        return (int(rnd)-1)*300 + int(m)*60 + int(s)
    except: return np.nan

fights['total_secs'] = fights.apply(lambda r: time_to_secs(r['Fight_Time'], r['Round']), axis=1)
fights.to_sql('fights', conn, if_exists='replace', index=False)

q5 = conn.execute("""
    SELECT 
        method_cat,
        COUNT(*) AS fights,
        ROUND(AVG(total_secs) / 60.0, 1) AS avg_minutes,
        ROUND(AVG(Round), 2) AS avg_round
    FROM fights
    WHERE "Win/No Contest/Draw" = 'win'
      AND total_secs IS NOT NULL
      AND method_cat IN ('KO/TKO','Submission','Decision')
    GROUP BY method_cat
    ORDER BY avg_minutes
""").fetchall()

print("\n=== Q5: Average Fight Duration by Method ===")
for row in q5:
    print(f"  {row[0]:<14} {row[1]:>5} fights  Avg: {row[2]} min  Avg Round: {row[3]}")

# ── SQL Query 6: Fights per year trend ────────────────────────────────────
q6 = conn.execute("""
    SELECT 
        CAST(year AS INTEGER) AS yr,
        COUNT(*) AS fights,
        ROUND(100.0 * SUM(CASE WHEN method_cat != 'Decision' AND "Win/No Contest/Draw"='win' THEN 1 ELSE 0 END) / 
              NULLIF(SUM(CASE WHEN "Win/No Contest/Draw"='win' THEN 1 ELSE 0 END), 0), 1) AS finish_rate
    FROM fights
    WHERE year >= 2000 AND year <= 2025
    GROUP BY yr
    ORDER BY yr
""").fetchall()

print("\n=== Q6: UFC Growth + Finish Rate by Year ===")
for row in q6:
    bar = '█' * (row[1] // 30)
    print(f"  {row[0]}: {row[1]:>3} fights  Finish: {row[2]:>4}%  {bar}")

conn.close()
print("\nSQL analysis complete.")
