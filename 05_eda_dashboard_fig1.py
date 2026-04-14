import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')

ml = pd.read_csv('/home/claude/ml_dataset.csv')
fights = pd.read_csv('/home/claude/fights_clean.csv')
fighters = pd.read_csv('/home/claude/fighters_clean.csv')

# ─── FIGURE 1: Overview Dashboard ─────────────────────────────────────────
fig = plt.figure(figsize=(20, 24))
fig.patch.set_facecolor('#0d1117')

# Custom color palette
colors = ['#e63946','#457b9d','#2a9d8f','#e9c46a','#f4a261','#a8dadc']
GOLD = '#e9c46a'; RED = '#e63946'; BLUE = '#457b9d'; GREEN = '#2a9d8f'

gs = gridspec.GridSpec(4, 3, figure=fig, hspace=0.45, wspace=0.35,
                        top=0.95, bottom=0.04, left=0.07, right=0.97)

def style_ax(ax, title='', xlabel='', ylabel=''):
    ax.set_facecolor('#161b22')
    ax.tick_params(colors='#c9d1d9', labelsize=9)
    ax.spines['bottom'].set_color('#30363d')
    ax.spines['left'].set_color('#30363d')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if title: ax.set_title(title, color='#e6edf3', fontsize=11, fontweight='bold', pad=8)
    if xlabel: ax.set_xlabel(xlabel, color='#8b949e', fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, color='#8b949e', fontsize=9)
    return ax

# Title
fig.text(0.5, 0.975, 'UFC Fight Analytics  ·  Predicting Fight Outcomes', 
         ha='center', va='top', fontsize=22, fontweight='bold', color='#e6edf3')
fig.text(0.5, 0.962, '8,482 fights  ·  4,448 fighters  ·  756 events  ·  1994 – 2025',
         ha='center', va='top', fontsize=13, color=GOLD)

# ── Plot 1: Finish rate over time ──────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :2])
style_ax(ax1, 'Finish Rate by Year (KO/TKO + Submission)', 'Year', 'Finish Rate (%)')
fights['year'] = pd.to_datetime(fights['date']).dt.year
yr = fights[(fights['Win/No Contest/Draw']=='win') & (fights['year']>=1995) & (fights['year']<=2025)]
yr_fin = yr.groupby('year').apply(lambda x: (x['method_cat']!='Decision').mean()*100).reset_index()
yr_fin.columns = ['year','finish_rate']
ax1.fill_between(yr_fin['year'], yr_fin['finish_rate'], alpha=0.25, color=RED)
ax1.plot(yr_fin['year'], yr_fin['finish_rate'], color=RED, lw=2.5, marker='o', markersize=4)
ax1.axhline(yr_fin['finish_rate'].mean(), color=GOLD, ls='--', lw=1.5, alpha=0.8, label=f"Avg: {yr_fin['finish_rate'].mean():.1f}%")
ax1.legend(facecolor='#161b22', labelcolor='#c9d1d9', fontsize=9)
ax1.set_xlim(1995, 2025)

# ── Plot 2: Finish method pie ──────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 2])
style_ax(ax2, 'Finish Methods')
w = fights[fights['Win/No Contest/Draw']=='win']
mc = w['method_cat'].value_counts()
wedge_colors = [RED, BLUE, GREEN, GOLD]
wedges, texts, autotexts = ax2.pie(mc.values, labels=mc.index, autopct='%1.1f%%',
    colors=wedge_colors[:len(mc)], startangle=140, textprops={'color':'#c9d1d9','fontsize':9},
    wedgeprops={'edgecolor':'#0d1117','linewidth':2})
for at in autotexts: at.set_color('#e6edf3'); at.set_fontsize(9)

# ── Plot 3: Top submission types ──────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
style_ax(ax3, 'Top Submissions', 'Count', '')
subs = fights[fights['method_cat']=='Submission']['Method'].str.replace('SUB ','').value_counts().head(8)
bars = ax3.barh(subs.index[::-1], subs.values[::-1], color=GREEN, alpha=0.85, height=0.6)
for b, v in zip(bars, subs.values[::-1]):
    ax3.text(b.get_width()+5, b.get_y()+b.get_height()/2, str(v), va='center', color='#8b949e', fontsize=8)
ax3.set_xlim(0, subs.max()*1.2)

# ── Plot 4: Top KO methods ────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
style_ax(ax4, 'Top KO/TKO Methods', 'Count', '')
kos = fights[fights['method_cat']=='KO/TKO']['Method'].str.replace('KO/TKO ','').value_counts().head(8)
bars = ax4.barh(kos.index[::-1], kos.values[::-1], color=RED, alpha=0.85, height=0.6)
for b, v in zip(bars, kos.values[::-1]):
    ax4.text(b.get_width()+5, b.get_y()+b.get_height()/2, str(v), va='center', color='#8b949e', fontsize=8)
ax4.set_xlim(0, kos.max()*1.2)

# ── Plot 5: Finish rate by weight class ──────────────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
style_ax(ax5, 'Finish Rate by Weight Class', '', 'Finish Rate (%)')
wc_order = ['Strawweight',"Women's Strawweight","Women's Flyweight",'Flyweight','Bantamweight',
            'Featherweight','Lightweight','Welterweight','Middleweight','Light Heavyweight','Heavyweight']
wc_df = w.groupby('Weight_Class').apply(lambda x: (x['method_cat']!='Decision').mean()*100)
wc_df = wc_df.reindex([x for x in wc_order if x in wc_df.index])
bar_colors = [RED if v > 55 else BLUE for v in wc_df.values]
ax5.barh(wc_df.index, wc_df.values, color=bar_colors, alpha=0.85, height=0.65)
ax5.axvline(50, color=GOLD, ls='--', lw=1.2, alpha=0.7)
ax5.tick_params(axis='y', labelsize=7.5)

# ── Plot 6: Fighter stats distributions ──────────────────────────────────
ax6 = fig.add_subplot(gs[2, 0])
style_ax(ax6, 'Fighter Height Distribution', 'Height (inches)', 'Count')
ht = fighters['height_in'].dropna()
ax6.hist(ht, bins=25, color=BLUE, alpha=0.8, edgecolor='#0d1117')
ax6.axvline(ht.mean(), color=GOLD, ls='--', lw=2, label=f'Mean: {ht.mean():.1f}"')
ax6.legend(facecolor='#161b22', labelcolor='#c9d1d9', fontsize=9)

ax7 = fig.add_subplot(gs[2, 1])
style_ax(ax7, 'Fighter Reach Distribution', 'Reach (inches)', 'Count')
rc = fighters['reach_in'].dropna()
ax7.hist(rc, bins=25, color=GREEN, alpha=0.8, edgecolor='#0d1117')
ax7.axvline(rc.mean(), color=GOLD, ls='--', lw=2, label=f'Mean: {rc.mean():.1f}"')
ax7.legend(facecolor='#161b22', labelcolor='#c9d1d9', fontsize=9)

ax8 = fig.add_subplot(gs[2, 2])
style_ax(ax8, 'Win % vs. Reach Advantage', 'Reach Advantage (inches)', 'Win Rate')
ml_sub = ml[ml['reach_diff'].notna()].copy()
ml_sub['reach_bin'] = pd.cut(ml_sub['reach_diff'], bins=[-20,-10,-5,-1,1,5,10,20], labels=['-20→-10','-10→-5','-5→-1','~0','1→5','5→10','10→20'])
rb = ml_sub.groupby('reach_bin').size() / (ml_sub.groupby('reach_bin').size() + 0.01)
# just show raw win% by reach bucket (winner always 1, so use count proxy)
counts = ml_sub['reach_bin'].value_counts().sort_index()
# win% for winner (fighter1 won by definition) by bin
win_rate = ml_sub.groupby('reach_bin').apply(lambda x: len(x) / (len(x) * 2) * 2).reset_index()
ax8.bar(counts.index.astype(str), counts.values / counts.sum() * 100, color=GOLD, alpha=0.85)
ax8.set_xlabel('Reach Diff Bucket (Winner - Loser)', color='#8b949e', fontsize=8)
ax8.set_ylabel('% of Fights Won', color='#8b949e', fontsize=8)
plt.setp(ax8.xaxis.get_majorticklabels(), rotation=30, ha='right', fontsize=7)

# ── Plot 7: Round distribution ────────────────────────────────────────────
ax9 = fig.add_subplot(gs[3, 0])
style_ax(ax9, 'Fight-Ending Round Distribution', 'Round', 'Count')
rd = w['Round'].value_counts().sort_index()
ax9.bar(rd.index.astype(str), rd.values, color=colors, alpha=0.85, edgecolor='#0d1117')
for i,(idx,v) in enumerate(rd.items()):
    ax9.text(i, v+20, str(v), ha='center', color='#c9d1d9', fontsize=8)

# ── Plot 8: Strikes vs Outcome ────────────────────────────────────────────
ax10 = fig.add_subplot(gs[3, 1])
style_ax(ax10, 'Striking Advantage → Outcome', 'Str. Landed Diff (Winner–Loser)', 'Count')
sd = ml['str_diff'].dropna()
ax10.hist(sd[sd!=0], bins=40, color=BLUE, alpha=0.8, edgecolor='#0d1117')
ax10.axvline(0, color=RED, ls='--', lw=1.5)
ax10.axvline(sd.mean(), color=GOLD, ls='--', lw=2, label=f'Mean: +{sd.mean():.0f}')
ax10.legend(facecolor='#161b22', labelcolor='#c9d1d9', fontsize=9)

# ── Plot 9: Fighter record vs win pct ─────────────────────────────────────
ax11 = fig.add_subplot(gs[3, 2])
style_ax(ax11, 'Experience vs Win Rate', 'Career Fights', 'Win %')
flt = fighters[(fighters['total_fights']>=5) & (fighters['win_pct'].notna())]
sc = ax11.scatter(flt['total_fights'], flt['win_pct']*100, 
    c=flt['total_fights'], cmap='RdYlGn', alpha=0.4, s=20, linewidths=0)
ax11.set_xlim(0, 50); ax11.set_ylim(0, 105)
plt.colorbar(sc, ax=ax11, label='Fights', shrink=0.8).ax.yaxis.label.set_color('#8b949e')

plt.savefig('/home/claude/fig1_overview.png', dpi=150, bbox_inches='tight',
            facecolor='#0d1117', edgecolor='none')
plt.close()
print("Fig 1 saved")

