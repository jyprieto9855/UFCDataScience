import pandas as pd
import numpy as np
import json, warnings
warnings.filterwarnings('ignore')

fights   = pd.read_csv('/home/claude/fights_clean.csv')
fighters = pd.read_csv('/home/claude/fighters_clean.csv')
ml       = pd.read_csv('/home/claude/ml_dataset.csv')

with open('/home/claude/ml_results.json') as f:
    ml_results = json.load(f)

fights['year'] = pd.to_datetime(fights['date']).dt.year
w = fights[fights['Win/No Contest/Draw']=='win'].copy()

# ── SQL-style queries using pandas ────────────────────────────────────────
print("=== KEY STATISTICS ===")
print(f"Total fights: {len(fights):,}")
print(f"Total fighters: {len(fighters):,}")
print(f"Date range: {fights['date'].min()[:10]} → {fights['date'].max()[:10]}")
print(f"Overall finish rate: {(w['method_cat']!='Decision').mean()*100:.1f}%")
print(f"KO/TKO rate: {(w['method_cat']=='KO/TKO').mean()*100:.1f}%")
print(f"Submission rate: {(w['method_cat']=='Submission').mean()*100:.1f}%")

print("\n=== MODEL PERFORMANCE ===")
for name, r in ml_results.items():
    print(f"  {name}: Acc={r['acc']:.3f} | AUC={r['auc']:.3f} | CV-AUC={r['cv_auc']:.3f}")

print("\n=== STRIKING STATS ===")
str_win = ml['str_diff'].dropna()
print(f"Median striking advantage of winner: +{str_win.median():.0f} strikes")
print(f"% of fights won by out-striking opponent: {(str_win>0).mean()*100:.1f}%")

print("\n=== REACH ADVANTAGE ===")
rc = ml['reach_diff'].dropna()
print(f"Mean reach advantage of winner: +{rc.mean():.2f}\"")
print(f"% of fights won by longer-reach fighter: {(rc>0).mean()*100:.1f}%")

