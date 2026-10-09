# Retail Business Intelligence & Customer Risk Analytics

## Overview
A Python + Streamlit dashboard for turning raw tabular data into business-oriented analysis: KPIs, trends, category/region drivers, risk screening, cleaning, and recommendations.

## Features
- CSV and Excel upload
- Synthetic demo dataset for testing
- Duplicate removal and missing-value handling
- Executive KPI summary and trend charts
- Category/product and regional comparisons
- Optional percentile-based risk screening when a numeric risk field exists
- Data-quality profile, descriptive statistics, and correlation heatmap
- CSV downloads for cleaned data and high-risk records

## Stack
Python, Streamlit, Pandas, NumPy, Plotly, OpenPyXL.

## Dataset
The built-in demo data is synthetic. For final internship submission, use a dataset different from the exact dataset used in the masterclasses and fill in the details below:
- Dataset name: [enter name]
- Dataset source URL: [paste the actual URL]
- License/usage notes: [if available]

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Optional virtual environment (Windows):
   `python -m venv .venv`
   `.venv\Scripts\activate`
4. Install packages: `pip install -r requirements.txt`
5. Start the app: `streamlit run app.py`
6. Open the local URL shown in the terminal (usually `http://localhost:8501`).

## How to use
Choose demo data or upload CSV/XLSX in the sidebar. Verify the field mappings in the sidebar, then inspect each tab and download the cleaned dataset as needed.

## Methodology
Load data → inspect and clean → map KPIs → analyze trends and categories → screen risk if a relevant field exists → make recommendations for investigation/action.

## Limitations
- Field mapping is heuristic and must be checked.
- High-risk records are identified using the 75th percentile of an existing numeric field; this is not a trained or validated prediction model.
- Insight text is rule-based; no external generative AI API is called.
- Median/mode imputation can affect the distribution of values.
- Synthetic demo data must not be represented as real business data.

## Submission files
- `app.py`: complete Python application (UI and analysis logic)
- `requirements.txt`: dependencies
- `README.md`: project overview and dataset source
- `project_report.docx`: report template; add real screenshots after running the app

## Future work
Add validated forecasting/churn models if a suitable labeled dataset is selected, configurable KPI targets, tests, and an optional AI API integration with secure key handling.
