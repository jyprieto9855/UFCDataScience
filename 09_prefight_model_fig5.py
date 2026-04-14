import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, learning_curve
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, roc_curve, precision_recall_curve, average_precision_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.calibration import calibration_curve
import warnings
warnings.filterwarnings('ignore')

BG='#0d1117'; PANEL='#161b22'; BORDER='#30363d'
GOLD='#e9c46a'; RED='#e63946'; BLUE='#457b9d'; GREEN='#2a9d8f'
PURPLE='#9b5de5'; TEXT='#e6edf3'; DIM='#8b949e'

ml = pd.read_csv('/home/claude/ml_dataset.csv')
fights = pd.read_csv('/home/claude/fights_clean.csv')

def style_ax(ax, title='', xlabel='', ylabel=''):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors='#c9d1d9', labelsize=9)
    for sp in ['bottom','left']: ax.spines[sp].set_color(BORDER)
    for sp in ['top','right']:   ax.spines[sp].set_visible(False)
    if title: ax.set_title(title, color=TEXT, fontsize=11, fontweight='bold', pad=8)
    if xlabel: ax.set_xlabel(xlabel, color=DIM, fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, color=DIM, fontsize=9)

# ── Pre-fight only features (no in-fight stats) ────────────────────────────
pre_feats = ['height_diff','reach_diff','win_pct_diff','exp_diff','stance_f1','stance_f2']

ml_pre = ml[pre_feats].copy()
ml_mirror = ml[pre_feats].copy()
ml_mirror['height_diff']  *= -1
ml_mirror['reach_diff']   *= -1
ml_mirror['win_pct_diff'] *= -1
ml_mirror['exp_diff']     *= -1
ml_mirror[['stance_f1','stance_f2']] = ml_mirror[['stance_f2','stance_f1']].values

X_pre = pd.concat([ml_pre, ml_mirror], ignore_index=True)
y_pre = np.array([1]*len(ml_pre) + [0]*len(ml_mirror))
mask  = X_pre.notna().all(axis=1)
X_pre, y_pre = X_pre[mask], y_pre[mask]

# Full features (in-fight included)
full_feats = ['height_diff','reach_diff','win_pct_diff','exp_diff',
              'kd_diff','str_diff','td_diff','sub_diff','stance_f1','stance_f2']
ml_full = ml[full_feats].copy()
ml_full_m = ml[full_feats].copy()
for c in ['height_diff','reach_diff','win_pct_diff','exp_diff','kd_diff','str_diff','td_diff','sub_diff']:
    ml_full_m[c] *= -1
ml_full_m[['stance_f1','stance_f2']] = ml_full_m[['stance_f2','stance_f1']].values
X_full = pd.concat([ml_full, ml_full_m], ignore_index=True)
y_full = np.array([1]*len(ml_full) + [0]*len(ml_full_m))
mask2  = X_full.notna().all(axis=1)
X_full, y_full = X_full[mask2], y_full[mask2]

# Train both
X_tr_p, X_te_p, y_tr_p, y_te_p = train_test_split(X_pre, y_pre, test_size=0.2, random_state=42, stratify=y_pre)
X_tr_f, X_te_f, y_tr_f, y_te_f = train_test_split(X_full, y_full, test_size=0.2, random_state=42, stratify=y_full)

pipe_pre = Pipeline([('imp', SimpleImputer()), ('sc', StandardScaler()),
                     ('clf', GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42))])
pipe_full = Pipeline([('imp', SimpleImputer()), ('sc', StandardScaler()),
                      ('clf', GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42))])

pipe_pre.fit(X_tr_p, y_tr_p)
pipe_full.fit(X_tr_f, y_tr_f)

prob_pre  = pipe_pre.predict_proba(X_te_p)[:,1]
prob_full = pipe_full.predict_proba(X_te_f)[:,1]

auc_pre  = roc_auc_score(y_te_p, prob_pre)
auc_full = roc_auc_score(y_te_f, prob_full)
print(f"Pre-fight model AUC: {auc_pre:.4f}")
print(f"Full model AUC:      {auc_full:.4f}")

# Learning curves
train_sizes, train_scores, val_scores = learning_curve(
    pipe_pre, X_pre, y_pre, cv=5, scoring='roc_auc',
    train_sizes=np.linspace(0.1, 1.0, 10), n_jobs=-1)

# ── FIGURE 5 ──────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 18))
fig.patch.set_facecolor(BG)
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35,
                        top=0.93, bottom=0.07, left=0.07, right=0.97)

fig.text(0.5, 0.965, 'Model Depth Analysis: Pre-Fight vs. Full Model', 
         ha='center', va='top', fontsize=18, fontweight='bold', color=TEXT)
fig.text(0.5, 0.950, 'Pre-fight prediction  ·  Learning curves  ·  Calibration  ·  Precision-Recall  ·  Statistical tests',
         ha='center', va='top', fontsize=11, color=GOLD)

# ── 1: ROC comparison pre vs full ─────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
style_ax(ax1, 'Pre-Fight vs. Full Model ROC', 'FPR', 'TPR')
for y_te, probs, label, color in [
    (y_te_p, prob_pre,  f'Pre-Fight Only (AUC={auc_pre:.3f})',  GOLD),
    (y_te_f, prob_full, f'Full Stats (AUC={auc_full:.3f})',      GREEN),
]:
    fpr, tpr, _ = roc_curve(y_te, probs)
    ax1.plot(fpr, tpr, color=color, lw=2.5, label=label)
ax1.plot([0,1],[0,1], color=BORDER, ls='--', lw=1.5)
ax1.legend(facecolor=PANEL, labelcolor='#c9d1d9', fontsize=8.5, loc='lower right')
ax1.set_xlim(0,1); ax1.set_ylim(0,1)
ax1.fill_between([0,1],[0,1], alpha=0.05, color='white')

# ── 2: Learning curve ─────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
style_ax(ax2, 'Learning Curve (Pre-Fight GB Model)', 'Training Examples', 'ROC-AUC')
tr_mean = train_scores.mean(axis=1)
tr_std  = train_scores.std(axis=1)
va_mean = val_scores.mean(axis=1)
va_std  = val_scores.std(axis=1)
ax2.plot(train_sizes, tr_mean, color=BLUE, lw=2, label='Train AUC')
ax2.fill_between(train_sizes, tr_mean-tr_std, tr_mean+tr_std, alpha=0.15, color=BLUE)
ax2.plot(train_sizes, va_mean, color=RED, lw=2, label='Val AUC')
ax2.fill_between(train_sizes, va_mean-va_std, va_mean+va_std, alpha=0.15, color=RED)
ax2.legend(facecolor=PANEL, labelcolor='#c9d1d9', fontsize=9)
ax2.set_ylim(0.5, 0.75)
ax2.axhline(va_mean[-1], color=GOLD, ls='--', lw=1.5, alpha=0.7, label=f'Converged: {va_mean[-1]:.3f}')

# ── 3: Calibration curve ──────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
style_ax(ax3, 'Probability Calibration (Pre-Fight)', 'Mean Predicted Probability', 'Fraction of Positives')
frac_pos, mean_pred = calibration_curve(y_te_p, prob_pre, n_bins=10)
ax3.plot(mean_pred, frac_pos, color=GOLD, lw=2.5, marker='o', markersize=6, label='GB Calibration')
ax3.plot([0,1],[0,1], color=BORDER, ls='--', lw=1.5, label='Perfect Calibration')
ax3.fill_between([0,1],[0,1], alpha=0.04, color='white')
ax3.legend(facecolor=PANEL, labelcolor='#c9d1d9', fontsize=9)

# ── 4: Precision-Recall ───────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 0])
style_ax(ax4, 'Precision-Recall Curve', 'Recall', 'Precision')
prec, rec, _ = precision_recall_curve(y_te_p, prob_pre)
ap = average_precision_score(y_te_p, prob_pre)
ax4.plot(rec, prec, color=PURPLE, lw=2.5, label=f'AP = {ap:.3f}')
ax4.axhline(0.5, color=BORDER, ls='--', lw=1.5, label='Baseline (0.50)')
ax4.fill_between(rec, prec, alpha=0.1, color=PURPLE)
ax4.legend(facecolor=PANEL, labelcolor='#c9d1d9', fontsize=9)

# ── 5: Confusion matrices side-by-side ────────────────────────────────────
from sklearn.metrics import confusion_matrix
ax5 = fig.add_subplot(gs[1, 1])
style_ax(ax5, 'Pre-Fight Model Confusion Matrix')
cm_pre = confusion_matrix(y_te_p, pipe_pre.predict(X_te_p))
sns.heatmap(cm_pre, annot=True, fmt='d', cmap='Blues', ax=ax5,
    linewidths=1, linecolor=BG, annot_kws={'size':14,'color':'#1a1a2e'},
    xticklabels=['Pred Loss','Pred Win'], yticklabels=['True Loss','True Win'],
    cbar_kws={'shrink':0.8})
ax5.tick_params(colors='#c9d1d9', labelsize=8)
pre_acc = (pipe_pre.predict(X_te_p)==y_te_p).mean()
ax5.text(0.5, -0.12, f'Accuracy: {pre_acc:.1%}  |  AUC: {auc_pre:.3f}',
         transform=ax5.transAxes, ha='center', color=GOLD, fontsize=9)

# ── 6: Feature importance comparison ──────────────────────────────────────
ax6 = fig.add_subplot(gs[1, 2])
style_ax(ax6, 'Pre-Fight Feature Importances', 'Importance', '')
clf_pre = pipe_pre.named_steps['clf']
fi = pd.Series(clf_pre.feature_importances_, index=pre_feats).sort_values(ascending=True)
feat_labels = {
    'win_pct_diff': 'Win% Differential',
    'exp_diff': 'Experience Diff',
    'reach_diff': 'Reach Differential',
    'height_diff': 'Height Differential',
    'stance_f2': 'Opponent Stance',
    'stance_f1': 'Winner Stance',
}
bar_c = [GREEN if v > fi.mean() else BLUE for v in fi.values]
ax6.barh([feat_labels.get(i,i) for i in fi.index], fi.values, color=bar_c, alpha=0.85, height=0.6)
for i, (idx, v) in enumerate(fi.items()):
    ax6.text(v+0.001, i, f'{v:.3f}', va='center', color=DIM, fontsize=8.5)

plt.savefig('/home/claude/fig5_prefight.png', dpi=150, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
plt.close()
print("Fig 5 saved.")
print(f"\nPre-fight model accuracy: {pre_acc:.4f}")
print(f"Average Precision Score: {ap:.4f}")

