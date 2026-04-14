import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

fights = pd.read_csv('/home/claude/fights_clean.csv')
fighters = pd.read_csv('/home/claude/fighters_clean.csv')
ml = pd.read_csv('/home/claude/ml_dataset.csv')

BG='#0d1117'; PANEL='#161b22'; BORDER='#30363d'
GOLD='#e9c46a'; RED='#e63946'; BLUE='#457b9d'; GREEN='#2a9d8f'
TEXT='#e6edf3'; DIM='#8b949e'

def style_ax(ax, title='', xlabel='', ylabel=''):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors='#c9d1d9', labelsize=9)
    for sp in ['bottom','left']: ax.spines[sp].set_color(BORDER)
    for sp in ['top','right']: ax.spines[sp].set_visible(False)
    if title: ax.set_title(title, color=TEXT, fontsize=11, fontweight='bold', pad=8)
    if xlabel: ax.set_xlabel(xlabel, color=DIM, fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, color=DIM, fontsize=9)

fig = plt.figure(figsize=(20, 20))
fig.patch.set_facecolor(BG)
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35,
                        top=0.94, bottom=0.05, left=0.07, right=0.97)

fig.text(0.5, 0.965, 'Deep Dive: Fighter Analytics & Statistical Insights', 
         ha='center', va='top', fontsize=18, fontweight='bold', color=TEXT)
fig.text(0.5, 0.950, 'Stance matchups  ·  Physical attributes  ·  Career trajectories  ·  Era analysis',
         ha='center', va='top', fontsize=11, color=GOLD)

fights['year'] = pd.to_datetime(fights['date']).dt.year
w = fights[fights['Win/No Contest/Draw']=='win'].copy()

# ── 1: Stance matchup heatmap ─────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
style_ax(ax1, 'Stance Matchup Win Rates', '', '')
stance_map = {'Orthodox':0,'Southpaw':1,'Switch':2,'Open Stance':3}
ml2 = ml.copy()
ml2['stance_f1_name'] = ml2['Stance_f1'].fillna('Unknown')
ml2['stance_f2_name'] = ml2['Stance_f2'].fillna('Unknown')
common = ['Orthodox','Southpaw','Switch']
sm = ml2[ml2['stance_f1_name'].isin(common) & ml2['stance_f2_name'].isin(common)]
# win% for f1 in each matchup (f1 always won)
pivot = sm.groupby(['stance_f1_name','stance_f2_name']).size().unstack(fill_value=0)
# normalise by total matchups
total = sm.groupby(['stance_f1_name']).size()
pivot_pct = pivot.div(total, axis=0) * 100
pivot_pct = pivot_pct.reindex(index=common, columns=common, fill_value=0)
sns.heatmap(pivot_pct, annot=True, fmt='.1f', cmap='RdYlGn', ax=ax1,
    linewidths=1, linecolor=BG, annot_kws={'size':11,'color':BG},
    cbar_kws={'shrink':0.8, 'label':'Win% as Winner'})
ax1.set_xlabel('Opponent Stance', color=DIM, fontsize=9)
ax1.set_ylabel('Winner Stance', color=DIM, fontsize=9)
ax1.tick_params(colors='#c9d1d9', labelsize=9)

# ── 2: Height vs reach correlation ────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
style_ax(ax2, 'Height vs Reach by Stance', 'Height (inches)', 'Reach (inches)')
stance_colors = {'Orthodox':BLUE,'Southpaw':RED,'Switch':GREEN,'Open Stance':GOLD}
for stance, color in stance_colors.items():
    sub = fighters[fighters['Stance']==stance].dropna(subset=['height_in','reach_in'])
    if len(sub) > 5:
        ax2.scatter(sub['height_in'], sub['reach_in'], c=color, alpha=0.35, s=15, label=stance)
corr_data = fighters.dropna(subset=['height_in','reach_in'])
corr = corr_data['height_in'].corr(corr_data['reach_in'])
m, b = np.polyfit(corr_data['height_in'], corr_data['reach_in'], 1)
xs = np.linspace(60, 82, 100)
ax2.plot(xs, m*xs+b, color=GOLD, lw=2, ls='--')
ax2.legend(facecolor=PANEL, labelcolor='#c9d1d9', fontsize=8)
ax2.text(0.05, 0.92, f'r = {corr:.3f}', transform=ax2.transAxes, color=GOLD, fontsize=10, fontweight='bold')

# ── 3: Win rate by stance ──────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
style_ax(ax3, 'Fighter Win Rate by Stance', 'Stance', 'Win Rate (%)')
stance_wr = fighters[fighters['total_fights']>=5].groupby('Stance')['win_pct'].mean().dropna()*100
stance_wr = stance_wr.reindex(['Orthodox','Southpaw','Switch','Open Stance']).dropna()
bar_colors = [BLUE, RED, GREEN, GOLD]
bars = ax3.bar(stance_wr.index, stance_wr.values, color=bar_colors[:len(stance_wr)], alpha=0.85, width=0.55)
for b in bars:
    ax3.text(b.get_x()+b.get_width()/2, b.get_height()+0.3, f'{b.get_height():.1f}%',
             ha='center', color='#c9d1d9', fontsize=10, fontweight='bold')
ax3.set_ylim(0, 70)
ax3.tick_params(axis='x', colors='#c9d1d9', labelsize=10)

# ── 4: Finishes over eras ─────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, :2])
style_ax(ax4, 'Fight Outcome Composition by Era', 'Year', 'Share of Fights (%)')
yr_method = w.groupby(['year','method_cat']).size().unstack(fill_value=0)
yr_method = yr_method.div(yr_method.sum(axis=1), axis=0)*100
yr_method = yr_method[(yr_method.index>=1995)&(yr_method.index<=2025)]
for col, c in zip(['KO/TKO','Submission','Decision'], [RED, GREEN, BLUE]):
    if col in yr_method.columns:
        ax4.plot(yr_method.index, yr_method[col], color=c, lw=2.5, label=col, marker='o', markersize=3)
        ax4.fill_between(yr_method.index, yr_method[col], alpha=0.08, color=c)
ax4.legend(facecolor=PANEL, labelcolor='#c9d1d9', fontsize=10)
ax4.set_xlim(1995, 2025)
# Annotate TRT era
ax4.axvspan(2009, 2015, alpha=0.08, color=GOLD, label='')
ax4.text(2012, 5, 'TRT Era\n(2009–2015)', ha='center', color=GOLD, fontsize=7.5, alpha=0.9)

# ── 5: Top weight classes fight volume ────────────────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
style_ax(ax5, 'Fights per Weight Class', 'Count', '')
wc = fights['Weight_Class'].value_counts().head(11)
colors_wc = [GOLD if 'Women' in x else BLUE for x in wc.index]
ax5.barh(wc.index[::-1], wc.values[::-1], color=colors_wc[::-1], alpha=0.85, height=0.65)
for i, (idx, v) in enumerate(wc[::-1].items()):
    ax5.text(v+10, i, str(v), va='center', color='#8b949e', fontsize=8)
ax5.tick_params(axis='y', labelsize=8.5)

# ── 6: Fighter career arc (top fighters by fight count) ───────────────────
ax6 = fig.add_subplot(gs[2, :2])
style_ax(ax6, 'Win % Trajectory: Most Active Fighters', 'Career Fight #', 'Cumulative Win %')
# Get most active fighters (by fight count in dataset)
fight_counts = pd.concat([
    fights[['Fighter_Id_1','date']].rename(columns={'Fighter_Id_1':'Fighter_Id'}),
    fights[['Fighter_Id_2','date']].rename(columns={'Fighter_Id_2':'Fighter_Id'})
]).dropna()
top_active = fight_counts['Fighter_Id'].value_counts().head(8).index.tolist()

cmap = plt.cm.tab10
for i, fid in enumerate(top_active):
    # Get all fights for this fighter in order
    f1 = fights[fights['Fighter_Id_1']==fid][['date','Fighter_Id_1','Win/No Contest/Draw']].copy()
    f1['won'] = (f1['Win/No Contest/Draw']=='win').astype(int)
    f2 = fights[fights['Fighter_Id_2']==fid][['date','Fighter_Id_2','Win/No Contest/Draw']].copy()
    f2['won'] = (f2['Win/No Contest/Draw']!='win').astype(int)  # f2 wins when f1 loses
    career = pd.concat([f1[['date','won']], f2[['date','won']]]).sort_values('date').reset_index(drop=True)
    career['cumwin'] = career['won'].cumsum() / (career.index + 1) * 100
    fname = fighters[fighters['Fighter_Id']==fid][['First','Last']].iloc[0] if len(fighters[fighters['Fighter_Id']==fid])>0 else None
    label = f"{fname['First']} {fname['Last']}" if fname is not None else fid[:8]
    ax6.plot(range(1, len(career)+1), career['cumwin'], color=cmap(i), lw=2, label=label, alpha=0.85)
ax6.legend(facecolor=PANEL, labelcolor='#c9d1d9', fontsize=7.5, ncol=2, loc='lower right')
ax6.set_xlim(1, 40); ax6.set_ylim(20, 100)
ax6.axhline(50, color=BORDER, ls='--', lw=1)

# ── 7: Knockdown % by weight class ────────────────────────────────────────
ax7 = fig.add_subplot(gs[2, 2])
style_ax(ax7, 'Avg. Knockdowns per Fight by Weight', '', 'Avg KDs')
kd_by_wc = w.groupby('Weight_Class')['KD_1'].mean().sort_values(ascending=False).head(10)
ax7.barh(kd_by_wc.index[::-1], kd_by_wc.values[::-1], color=RED, alpha=0.8, height=0.65)
ax7.tick_params(axis='y', labelsize=8.5)
ax7.set_xlabel('Average Knockdowns (Winner)', color=DIM, fontsize=9)

plt.savefig('/home/claude/fig3_deep.png', dpi=150, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
plt.close()
print("Fig 3 saved")

