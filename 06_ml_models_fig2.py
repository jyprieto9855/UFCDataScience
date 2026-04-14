import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
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

BG = '#0d1117'; PANEL = '#161b22'; BORDER = '#30363d'
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
    return ax

# ─── ML: Win Prediction ───────────────────────────────────────────────────
features = ['height_diff','reach_diff','win_pct_diff','exp_diff',
            'kd_diff','str_diff','td_diff','sub_diff','stance_f1','stance_f2']

ml_clean = ml[features].copy()
# Target: fighter1 always won (by design), so add mirror rows
ml_mirror = ml[features].copy()
ml_mirror['height_diff']  *= -1
ml_mirror['reach_diff']   *= -1
ml_mirror['win_pct_diff'] *= -1
ml_mirror['exp_diff']     *= -1
ml_mirror['kd_diff']      *= -1
ml_mirror['str_diff']     *= -1
ml_mirror['td_diff']      *= -1
ml_mirror['sub_diff']     *= -1
ml_mirror[['stance_f1','stance_f2']] = ml_mirror[['stance_f2','stance_f1']].values

X = pd.concat([ml_clean, ml_mirror], ignore_index=True)
y = np.array([1]*len(ml_clean) + [0]*len(ml_mirror))

# Remove NaN rows
mask = X.notna().all(axis=1)
X, y = X[mask], y[mask]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Three models
models = {
    'Logistic Regression': Pipeline([
        ('imp', SimpleImputer(strategy='median')),
        ('sc', StandardScaler()),
        ('clf', LogisticRegression(max_iter=500, random_state=42))
    ]),
    'Random Forest': Pipeline([
        ('imp', SimpleImputer(strategy='median')),
        ('clf', RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1))
    ]),
    'Gradient Boosting': Pipeline([
        ('imp', SimpleImputer(strategy='median')),
        ('clf', GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42))
    ])
}

results = {}
for name, pipe in models.items():
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:,1]
    cv = cross_val_score(pipe, X_train, y_train, cv=5, scoring='roc_auc', n_jobs=-1)
    results[name] = {
        'model': pipe, 'y_pred': y_pred, 'y_prob': y_prob,
        'auc': roc_auc_score(y_test, y_prob),
        'cv_auc': cv.mean(), 'cv_std': cv.std(),
        'acc': (y_pred==y_test).mean()
    }
    print(f"{name}: ACC={results[name]['acc']:.3f}  AUC={results[name]['auc']:.3f}  CV-AUC={cv.mean():.3f}±{cv.std():.3f}")

# Feature importance from RF
rf = results['Random Forest']['model'].named_steps['clf']
feat_imp = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=True)

# ─── FIGURE 2: ML Results ─────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 16))
fig.patch.set_facecolor(BG)
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35,
                        top=0.93, bottom=0.07, left=0.07, right=0.97)

fig.text(0.5, 0.965, 'Machine Learning: Fight Outcome Prediction', 
         ha='center', va='top', fontsize=18, fontweight='bold', color=TEXT)
fig.text(0.5, 0.950, 'Binary classification — who wins — using physical & record differentials',
         ha='center', va='top', fontsize=11, color=GOLD)

# ── ROC curves ──────────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
style_ax(ax1, 'ROC Curves', 'False Positive Rate', 'True Positive Rate')
model_colors = [BLUE, GREEN, RED]
for (name, r), c in zip(results.items(), model_colors):
    fpr, tpr, _ = roc_curve(y_test, r['y_prob'])
    ax1.plot(fpr, tpr, color=c, lw=2.5, label=f"{name} (AUC={r['auc']:.3f})")
ax1.plot([0,1],[0,1], color=BORDER, ls='--', lw=1.5)
ax1.legend(facecolor=PANEL, labelcolor='#c9d1d9', fontsize=8, loc='lower right')
ax1.set_xlim(0,1); ax1.set_ylim(0,1)

# ── Feature importance ────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
style_ax(ax2, 'Feature Importance (Random Forest)', 'Importance', '')
feat_labels = {
    'str_diff':'Strike Differential','win_pct_diff':'Win% Differential',
    'exp_diff':'Experience Diff','reach_diff':'Reach Differential',
    'kd_diff':'Knockdown Diff','td_diff':'Takedown Diff',
    'height_diff':'Height Diff','sub_diff':'Sub Attempt Diff',
    'stance_f2':'Loser Stance','stance_f1':'Winner Stance'
}
bar_cols = [GREEN if v > feat_imp.mean() else BLUE for v in feat_imp.values]
bars = ax2.barh([feat_labels.get(i,i) for i in feat_imp.index], feat_imp.values,
    color=bar_cols, alpha=0.85, height=0.65)
ax2.tick_params(axis='y', labelsize=8)

# ── Model comparison ──────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
style_ax(ax3, 'Model Comparison', '', 'Score')
model_names = list(results.keys())
short_names = ['Logistic\nRegression', 'Random\nForest', 'Gradient\nBoosting']
accs = [results[n]['acc'] for n in model_names]
aucs = [results[n]['auc'] for n in model_names]
cv_aucs = [results[n]['cv_auc'] for n in model_names]
x = np.arange(3)
w = 0.25
b1 = ax3.bar(x-w, accs, w, label='Accuracy', color=BLUE, alpha=0.85)
b2 = ax3.bar(x, aucs, w, label='Test AUC', color=GREEN, alpha=0.85)
b3 = ax3.bar(x+w, cv_aucs, w, label='CV AUC', color=GOLD, alpha=0.85)
ax3.set_xticks(x); ax3.set_xticklabels(short_names, color='#c9d1d9', fontsize=8)
ax3.set_ylim(0.5, 0.82)
ax3.legend(facecolor=PANEL, labelcolor='#c9d1d9', fontsize=8)
ax3.axhline(0.5, color=BORDER, ls='--', lw=1)
for bars_group in [b1,b2,b3]:
    for b in bars_group:
        ax3.text(b.get_x()+b.get_width()/2, b.get_height()+0.003,
                 f'{b.get_height():.3f}', ha='center', color='#c9d1d9', fontsize=7)

# ── Confusion matrix (best model = GB) ────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 0])
style_ax(ax4, 'Gradient Boosting Confusion Matrix')
best_name = max(results, key=lambda k: results[k]['auc'])
cm = confusion_matrix(y_test, results[best_name]['y_pred'])
sns.heatmap(cm, annot=True, fmt='d', cmap='RdYlGn', ax=ax4,
    linewidths=1, linecolor=BG, annot_kws={'size':13,'color':BG},
    xticklabels=['Predicted Loss','Predicted Win'],
    yticklabels=['Actual Loss','Actual Win'],
    cbar_kws={'shrink':0.8})
ax4.tick_params(colors='#c9d1d9', labelsize=8)

# ── Probability calibration ───────────────────────────────────────────────
ax5 = fig.add_subplot(gs[1, 1])
style_ax(ax5, 'Prediction Confidence Distribution', 'Predicted Win Probability', 'Count')
best = results[best_name]
ax5.hist(best['y_prob'][y_test==1], bins=30, color=GREEN, alpha=0.6, label='True Win', density=True)
ax5.hist(best['y_prob'][y_test==0], bins=30, color=RED, alpha=0.6, label='True Loss', density=True)
ax5.axvline(0.5, color=GOLD, ls='--', lw=2)
ax5.legend(facecolor=PANEL, labelcolor='#c9d1d9', fontsize=9)

# ── KO probability by striking diff ──────────────────────────────────────
ax6 = fig.add_subplot(gs[1, 2])
style_ax(ax6, 'Striking Advantage → Finish Type', 'Striking Differential Bucket', 'Finish Rate (%)')
fights['str_diff'] = fights['STR_1'] - fights['STR_2']
fights['year'] = pd.to_datetime(fights['date']).dt.year
w_fights = fights[fights['Win/No Contest/Draw']=='win'].copy()
w_fights['str_bin'] = pd.cut(w_fights['str_diff'], bins=[-300,-100,-30,-5,5,30,100,300],
    labels=['<-100','-100→-30','-30→-5','~Even','5→30','30→100','>100'])
by_bin = w_fights.groupby('str_bin')['method_cat'].value_counts(normalize=True).unstack().fillna(0)*100
by_bin = by_bin.reindex(columns=['KO/TKO','Submission','Decision','Other'], fill_value=0)
x_pos = np.arange(len(by_bin))
bottom = np.zeros(len(by_bin))
for col, c in zip(by_bin.columns, [RED, GREEN, BLUE, GOLD]):
    ax6.bar(x_pos, by_bin[col].values, bottom=bottom, color=c, alpha=0.85, label=col, width=0.7)
    bottom += by_bin[col].values
ax6.set_xticks(x_pos); ax6.set_xticklabels(by_bin.index.astype(str), rotation=30, ha='right', fontsize=7.5, color='#c9d1d9')
ax6.legend(facecolor=PANEL, labelcolor='#c9d1d9', fontsize=8, loc='upper left')
ax6.set_ylabel('Outcome Composition (%)', color=DIM, fontsize=9)

plt.savefig('/home/claude/fig2_ml.png', dpi=150, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
plt.close()
print("Fig 2 saved")

# Save results for report
import json
summary = {n: {'acc': round(r['acc'],4), 'auc': round(r['auc'],4), 'cv_auc': round(r['cv_auc'],4)} for n,r in results.items()}
with open('/home/claude/ml_results.json','w') as f:
    json.dump(summary, f, indent=2)
print("ML results:", summary)

