import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')

BG='#0d1117'; PANEL='#161b22'; BORDER='#30363d'
GOLD='#e9c46a'; RED='#e63946'; BLUE='#457b9d'; GREEN='#2a9d8f'
PURPLE='#9b5de5'; ORANGE='#f4a261'; PINK='#e76f51'
TEXT='#e6edf3'; DIM='#8b949e'

fighters = pd.read_csv('/home/claude/fighters_clean.csv')
fights   = pd.read_csv('/home/claude/fights_clean.csv')
ml       = pd.read_csv('/home/claude/ml_dataset.csv')

def style_ax(ax, title='', xlabel='', ylabel=''):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors='#c9d1d9', labelsize=9)
    for sp in ['bottom','left']: ax.spines[sp].set_color(BORDER)
    for sp in ['top','right']:   ax.spines[sp].set_visible(False)
    if title: ax.set_title(title, color=TEXT, fontsize=11, fontweight='bold', pad=8)
    if xlabel: ax.set_xlabel(xlabel, color=DIM, fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, color=DIM, fontsize=9)

# ── Build per-fighter career stats by aggregating fights ──────────────────
# Average stats from fights as winner
w1 = fights[fights['Win/No Contest/Draw']=='win'][['Fighter_Id_1','STR_1','TD_1','KD_1','SUB_1','method_cat']].copy()
w1.columns = ['Fighter_Id','str','td','kd','sub','method']

# Average stats from fights as loser
l2 = fights[fights['Win/No Contest/Draw']=='win'][['Fighter_Id_2','STR_2','TD_2','KD_2','SUB_2','method_cat']].copy()
l2.columns = ['Fighter_Id','str','td','kd','sub','method']

all_perf = pd.concat([w1, l2])
for c in ['str','td','kd','sub']:
    all_perf[c] = pd.to_numeric(all_perf[c], errors='coerce')

perf = all_perf.groupby('Fighter_Id').agg(
    avg_str=('str','mean'),
    avg_td=('td','mean'),
    avg_kd=('kd','mean'),
    avg_sub=('sub','mean'),
    n_fights=('str','count')
).reset_index()

# Finish method profile
method_piv = all_perf.groupby(['Fighter_Id','method']).size().unstack(fill_value=0)
method_piv = method_piv.div(method_piv.sum(axis=1), axis=0)
method_piv = method_piv.reindex(columns=['KO/TKO','Submission','Decision','Other'], fill_value=0)
method_piv.columns = ['pct_ko','pct_sub','pct_dec','pct_other']

# Merge with physical
cluster_df = perf.merge(
    fighters[['Fighter_Id','height_in','reach_in','win_pct','total_fights']],
    on='Fighter_Id', how='inner'
).merge(method_piv, on='Fighter_Id', how='left')

cluster_df = cluster_df[cluster_df['n_fights'] >= 5].copy()

# Features for clustering
feats = ['avg_str','avg_td','avg_kd','avg_sub','pct_ko','pct_sub','pct_dec','height_in','reach_in']
X = cluster_df[feats].copy()

imp = SimpleImputer(strategy='median')
sc  = StandardScaler()
Xc  = sc.fit_transform(imp.fit_transform(X))

# Elbow method
inertias = []
K_range  = range(2, 9)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(Xc)
    inertias.append(km.inertia_)

# Fit k=5 clusters
km = KMeans(n_clusters=5, random_state=42, n_init=20)
cluster_df['cluster'] = km.fit_predict(Xc)

# PCA for 2D visualisation
pca = PCA(n_components=2, random_state=42)
Xpca = pca.fit_transform(Xc)
cluster_df['pca1'] = Xpca[:,0]
cluster_df['pca2'] = Xpca[:,1]

# Label clusters by dominant style
cluster_profiles = cluster_df.groupby('cluster')[feats].mean()
print("Cluster profiles:")
print(cluster_profiles.round(2))

# Name clusters manually based on profile
cluster_names = {
    cluster_profiles['pct_ko'].idxmax(): 'Power Strikers',
    cluster_profiles['pct_sub'].idxmax(): 'Submission Specialists',
    cluster_profiles['avg_td'].idxmax(): 'Dominant Wrestlers',
    cluster_profiles['pct_dec'].idxmax(): 'Decision Fighters',
}
remaining = [c for c in range(5) if c not in cluster_names]
if remaining:
    cluster_names[remaining[0]] = 'All-Round Athletes'
cluster_df['archetype'] = cluster_df['cluster'].map(cluster_names)
print("\nCluster sizes:")
print(cluster_df['archetype'].value_counts())

# ── FIGURE 4: Clustering + Advanced Analytics ─────────────────────────────
fig = plt.figure(figsize=(20, 22))
fig.patch.set_facecolor(BG)
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35,
                        top=0.94, bottom=0.05, left=0.07, right=0.97)

fig.text(0.5, 0.965, 'Fighter Archetypes & Advanced Analytics', 
         ha='center', va='top', fontsize=18, fontweight='bold', color=TEXT)
fig.text(0.5, 0.950, 'K-Means clustering · PCA projection · Career analysis · SQL insights',
         ha='center', va='top', fontsize=11, color=GOLD)

archetype_colors = {
    'Power Strikers': RED,
    'Submission Specialists': GREEN,
    'Dominant Wrestlers': BLUE,
    'Decision Fighters': GOLD,
    'All-Round Athletes': PURPLE
}

# ── 1: PCA scatter ────────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :2])
style_ax(ax1, 'Fighter Archetypes — PCA Projection (K-Means, k=5)', 'Principal Component 1', 'Principal Component 2')
for arch, color in archetype_colors.items():
    sub = cluster_df[cluster_df['archetype']==arch]
    ax1.scatter(sub['pca1'], sub['pca2'], c=color, alpha=0.35, s=18, label=arch)
# Cluster centroids
centers_pca = pca.transform(km.cluster_centers_)
for i, (cx, cy) in enumerate(centers_pca):
    arch = cluster_names.get(i, f'Cluster {i}')
    ax1.scatter(cx, cy, c=archetype_colors.get(arch, 'white'), s=180, edgecolors='white', linewidths=2, zorder=5, marker='*')
ax1.legend(facecolor=PANEL, labelcolor='#c9d1d9', fontsize=9, markerscale=1.5)
ax1.text(0.02, 0.95, f'PCA Var Explained: PC1={pca.explained_variance_ratio_[0]*100:.1f}%, PC2={pca.explained_variance_ratio_[1]*100:.1f}%',
         transform=ax1.transAxes, color=DIM, fontsize=8)

# ── 2: Elbow curve ────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 2])
style_ax(ax2, 'K-Means Elbow Curve', 'Number of Clusters (k)', 'Inertia')
ax2.plot(list(K_range), inertias, color=GOLD, lw=2.5, marker='o', markersize=7, markerfacecolor=RED)
ax2.axvline(5, color=RED, ls='--', lw=1.5, alpha=0.7, label='k=5 (chosen)')
ax2.legend(facecolor=PANEL, labelcolor='#c9d1d9', fontsize=9)

# ── 3: Archetype radar / bar profiles ─────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
style_ax(ax3, 'Archetype Fight Style Profiles', '', 'Normalized Value')
profile_feats = ['avg_str','avg_td','avg_kd','pct_ko','pct_sub','pct_dec']
profile_labels = ['Str/Fight','TD/Fight','KD/Fight','KO%','Sub%','Dec%']
profile_norm = cluster_df.groupby('archetype')[profile_feats].mean()
profile_norm = (profile_norm - profile_norm.min()) / (profile_norm.max() - profile_norm.min() + 1e-9)
x_pos = np.arange(len(profile_labels))
width = 0.15
for i, (arch, color) in enumerate(archetype_colors.items()):
    if arch in profile_norm.index:
        ax3.bar(x_pos + i*width, profile_norm.loc[arch].values, width, color=color, alpha=0.85, label=arch)
ax3.set_xticks(x_pos + width*2)
ax3.set_xticklabels(profile_labels, rotation=25, ha='right', color='#c9d1d9', fontsize=8)
ax3.legend(facecolor=PANEL, labelcolor='#c9d1d9', fontsize=7, ncol=1, loc='upper right')

# ── 4: Win rate by archetype ──────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
style_ax(ax4, 'Win Rate by Fighter Archetype', '', 'Average Win % (%)')
wr = cluster_df.groupby('archetype')['win_pct'].mean().sort_values(ascending=False) * 100
colors_wr = [archetype_colors.get(a, 'white') for a in wr.index]
bars = ax4.bar(range(len(wr)), wr.values, color=colors_wr, alpha=0.85, width=0.6)
ax4.set_xticks(range(len(wr)))
ax4.set_xticklabels([a.replace(' ','\n') for a in wr.index], color='#c9d1d9', fontsize=8)
for b, v in zip(bars, wr.values):
    ax4.text(b.get_x()+b.get_width()/2, v+0.3, f'{v:.1f}%', ha='center', color='#c9d1d9', fontsize=9, fontweight='bold')
ax4.set_ylim(0, 85)

# ── 5: Archetype size ─────────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
style_ax(ax5, 'Archetype Population', '', 'Number of Fighters')
sz = cluster_df['archetype'].value_counts()
ax5.pie(sz.values, labels=sz.index, colors=[archetype_colors.get(a,'grey') for a in sz.index],
    autopct='%1.0f%%', startangle=90, textprops={'color':'#c9d1d9','fontsize':8},
    wedgeprops={'edgecolor':'#0d1117','linewidth':2})

# ── 6: UFC Fight Volume Growth ────────────────────────────────────────────
ax6 = fig.add_subplot(gs[2, :2])
style_ax(ax6, 'UFC Event Growth & Finish Rate by Year (2000–2025)', 'Year', '')
fights['date'] = pd.to_datetime(fights['date'])
yr_stats = fights[fights['date'].dt.year.between(2000,2025)].copy()
yr_stats['year'] = yr_stats['date'].dt.year
yr_grp = yr_stats.groupby('year').agg(
    total=('Fight_Id','count'),
    finishes=('method_cat', lambda x: (x!='Decision').sum())
).reset_index()
yr_grp['finish_rate'] = yr_grp['finishes'] / yr_grp['total'].replace(0,np.nan) * 100

ax6b = ax6.twinx()
ax6.bar(yr_grp['year'], yr_grp['total'], color=BLUE, alpha=0.45, label='Total Fights')
ax6b.plot(yr_grp['year'], yr_grp['finish_rate'], color=RED, lw=2.5, marker='o', markersize=4, label='Finish Rate %')
ax6.set_ylabel('Total Fights', color=BLUE, fontsize=9)
ax6b.set_ylabel('Finish Rate (%)', color=RED, fontsize=9)
ax6b.tick_params(colors='#c9d1d9', labelsize=9)
ax6b.set_facecolor(PANEL)
ax6b.spines['right'].set_color(BORDER)
ax6b.spines['top'].set_visible(False)
lines1, labs1 = ax6.get_legend_handles_labels()
lines2, labs2 = ax6b.get_legend_handles_labels()
ax6.legend(lines1+lines2, labs1+labs2, facecolor=PANEL, labelcolor='#c9d1d9', fontsize=9)
ax6.set_xlim(1999, 2026)

# ── 7: Avg fight duration by method and era ───────────────────────────────
ax7 = fig.add_subplot(gs[2, 2])
style_ax(ax7, 'Avg Fight Duration by Outcome', 'Finish Method', 'Avg Duration (min)')
dur_data = fights[fights['Win/No Contest/Draw']=='win'].copy()
dur_data['total_secs'] = dur_data.apply(
    lambda r: (int(r['Round'])-1)*300 + (int(str(r['Fight_Time']).split(':')[0])*60 +
               int(str(r['Fight_Time']).split(':')[1])) if ':' in str(r['Fight_Time']) else np.nan, axis=1)
dur_by_method = dur_data.groupby('method_cat')['total_secs'].mean().dropna() / 60
dur_by_method = dur_by_method.reindex(['KO/TKO','Submission','Decision']).dropna()
bar_colors = [RED, GREEN, BLUE]
bars = ax7.bar(dur_by_method.index, dur_by_method.values, color=bar_colors, alpha=0.85, width=0.5)
for b, v in zip(bars, dur_by_method.values):
    mins, secs = int(v), int((v - int(v)) * 60)
    ax7.text(b.get_x()+b.get_width()/2, v+0.1, f'{mins}:{secs:02d}', ha='center', color='#c9d1d9', fontsize=10, fontweight='bold')
ax7.set_ylim(0, 20)
ax7.tick_params(axis='x', colors='#c9d1d9', labelsize=10)

plt.savefig('/home/claude/fig4_clusters.png', dpi=150, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
plt.close()
print("Fig 4 saved.")

# Save archetype stats for report
arch_stats = cluster_df.groupby('archetype').agg(
    count=('Fighter_Id','count'),
    avg_win_pct=('win_pct','mean'),
    avg_fights=('total_fights','mean'),
    avg_str=('avg_str','mean'),
    avg_td=('avg_td','mean'),
    pct_ko=('pct_ko','mean'),
    pct_sub=('pct_sub','mean')
).round(3)
print("\nArchetype summary:")
print(arch_stats)

