import sqlite3, pandas as pd
conn = sqlite3.connect('/home/claude/ufc.db')
q6 = conn.execute("""
    SELECT 
        CAST(substr(date, 1, 4) AS INTEGER) AS yr,
        COUNT(*) AS total_fights,
        SUM(CASE WHEN "Win/No Contest/Draw"='win' THEN 1 ELSE 0 END) AS wins,
        ROUND(100.0 * SUM(CASE WHEN method_cat != 'Decision' AND "Win/No Contest/Draw"='win' THEN 1 ELSE 0 END) / 
              NULLIF(SUM(CASE WHEN "Win/No Contest/Draw"='win' THEN 1 ELSE 0 END), 0), 1) AS finish_rate
    FROM fights
    WHERE date IS NOT NULL AND substr(date,1,4) >= '2000' AND substr(date,1,4) <= '2025'
    GROUP BY yr
    ORDER BY yr
""").fetchall()

print("=== Q6: UFC Growth + Finish Rate by Year ===")
for row in q6:
    bar = '█' * (row[1] // 25)
    print(f"  {row[0]}: {row[1]:>3} fights  Finish: {str(row[3]):>5}%  {bar}")
conn.close()
