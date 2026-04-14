# UFC Fight Analytics — Code Files

## Run Order
| File | Description |
|------|-------------|
| 01_build_features.py       | Data cleaning, feature engineering, builds ml_dataset.csv |
| 02_data_exploration.py     | Initial data inspection |
| 03_sql_analysis.py         | Builds SQLite DB + runs SQL queries 1–5 |
| 04_sql_query6_yearly.py    | SQL query 6: fight volume + finish rate by year |
| 05_eda_dashboard_fig1.py   | EDA overview dashboard (Figure 1) |
| 06_ml_models_fig2.py       | Trains 3 ML models, generates Figure 2 |
| 07_deep_dive_fig3.py       | Deep dive analytics, Figure 3 |
| 08_clustering_fig4.py      | K-Means clustering + archetypes, Figure 4 |
| 09_prefight_model_fig5.py  | Pre-fight vs full model comparison, Figure 5 |
| 10_compile_stats.py        | Compiles key stats for report |
| 11_generate_report.js      | Generates final Word report (Node.js) |

## Requirements
### Python
pip install pandas numpy matplotlib seaborn scikit-learn

### Node.js (for report generation)
npm install -g docx

## Data Files Expected
Place these in the same directory or update paths:
- raw_fights.csv
- raw_fighters.csv
- raw_events.csv
- raw_details.csv
- raw_fights_detailed.csv
