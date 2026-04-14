import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

fights   = pd.read_csv('/mnt/user-data/uploads/raw_fights.csv')
fighters = pd.read_csv('/mnt/user-data/uploads/raw_fighters.csv')
events   = pd.read_csv('/mnt/user-data/uploads/raw_events.csv')

# Force numeric
for c in ['KD_1','KD_2','STR_1','STR_2','TD_1','TD_2','SUB_1','SUB_2','Round']:
    fights[c] = pd.to_numeric(fights[c], errors='coerce')

def parse_height(h):
    try:
        parts = str(h).replace('"','').split("' ")
        return int(parts[0])*12 + int(parts[1])
    except: return np.nan

def parse_reach(r):
    try: return float(str(r).replace('"',''))
    except: return np.nan

def parse_weight(w):
    try: return float(str(w).replace(' lbs.',''))
    except: return np.nan

fighters['height_in']  = fighters['Ht.'].apply(parse_height)
fighters['reach_in']   = fighters['Reach'].apply(parse_reach)
fighters['weight_lbs'] = fighters['Wt.'].apply(parse_weight)
fighters['total_fights'] = fighters['W'] + fighters['L'] + fighters['D']
fighters['win_pct'] = fighters['W'] / fighters['total_fights'].replace(0, np.nan)

def method_cat(m):
    m = str(m)
    if 'KO' in m or 'TKO' in m: return 'KO/TKO'
    if 'SUB' in m: return 'Submission'
    if 'DEC' in m: return 'Decision'
    return 'Other'
fights['method_cat'] = fights['Method'].apply(method_cat)

events['date'] = pd.to_datetime(events['Date'])
fights = fights.merge(events[['Event_Id','date']], on='Event_Id', how='left')
fights = fights.sort_values('date').reset_index(drop=True)

wins_only = fights[fights['Win/No Contest/Draw'] == 'win'].copy()

f1 = fighters.rename(columns={c: c+'_f1' for c in fighters.columns if c != 'Fighter_Id'})
f2 = fighters.rename(columns={c: c+'_f2' for c in fighters.columns if c != 'Fighter_Id'})

ml = wins_only.merge(f1, left_on='Fighter_Id_1', right_on='Fighter_Id', how='left')
ml = ml.merge(f2, left_on='Fighter_Id_2', right_on='Fighter_Id', how='left')

ml['height_diff']  = ml['height_in_f1'] - ml['height_in_f2']
ml['reach_diff']   = ml['reach_in_f1']  - ml['reach_in_f2']
ml['win_pct_diff'] = ml['win_pct_f1']   - ml['win_pct_f2']
ml['exp_diff']     = ml['total_fights_f1'] - ml['total_fights_f2']
ml['kd_diff']      = ml['KD_1'] - ml['KD_2']
ml['str_diff']     = ml['STR_1'] - ml['STR_2']
ml['td_diff']      = ml['TD_1'] - ml['TD_2']
ml['sub_diff']     = ml['SUB_1'] - ml['SUB_2']

stance_map = {'Orthodox': 0, 'Southpaw': 1, 'Switch': 2, 'Open Stance': 3}
ml['stance_f1'] = ml['Stance_f1'].map(stance_map).fillna(-1)
ml['stance_f2'] = ml['Stance_f2'].map(stance_map).fillna(-1)

ml.to_csv('/home/claude/ml_dataset.csv', index=False)
fights.to_csv('/home/claude/fights_clean.csv', index=False)
fighters.to_csv('/home/claude/fighters_clean.csv', index=False)

print("Saved. ML shape:", ml.shape)
print("Date range:", fights['date'].min(), "→", fights['date'].max())
print("Method distribution:\n", fights['method_cat'].value_counts())
print("Finish rate:", round((1 - fights[fights['Win/No Contest/Draw']=='win']['method_cat'].eq('Decision').mean())*100,1), "%")
