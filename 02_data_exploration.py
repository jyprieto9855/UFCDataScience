import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')

# ─── Load Data ───────────────────────────────────────────────────────────────
fights    = pd.read_csv('/mnt/user-data/uploads/raw_fights.csv')
fighters  = pd.read_csv('/mnt/user-data/uploads/raw_fighters.csv')
events    = pd.read_csv('/mnt/user-data/uploads/raw_events.csv')
details   = pd.read_csv('/mnt/user-data/uploads/raw_details.csv')

print("Shapes:", fights.shape, fighters.shape, events.shape)
print("Win types:", fights['Win/No Contest/Draw'].value_counts().to_dict())
print("Methods:", fights['Method'].value_counts().to_dict())
print("Weight classes:", fights['Weight_Class'].value_counts().head(10).to_dict())

