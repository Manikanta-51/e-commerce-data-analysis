# E-commerce Data Analysis

Exploratory analysis of e-commerce data to understand **product performance** and **customer behaviour**, and to turn raw order data into business recommendations.

## What this project does
- **Cleans** order data (duplicates, missing quantities) and joins orders, customers and products
- Computes core **KPIs**: revenue, average order value, return and cancellation rates, repeat-customer rate, ratings
- Analyses **product performance** by category (revenue, units, ratings, return rate)
- Studies **customer behaviour**: monthly and seasonal trends, revenue by city, **RFM segmentation** (Champions / Loyal / Regular / At risk)
- Generates **charts** and a written **insights report** with recommendations

## Project structure
```
ecommerce-data-analysis/
├── data/
│   ├── raw/          # orders.csv, customers.csv, products.csv
│   └── processed/    # clean_orders.csv (generated)
├── src/
│   ├── generate_data.py   # synthetic dataset generator
│   └── analysis.py        # cleaning, KPIs, RFM, charts, report
├── reports/
│   ├── figures/      # PNG charts (generated)
│   └── insights.md   # findings and recommendations (generated)
├── requirements.txt
└── README.md
```

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/generate_data.py    # creates data/raw/*.csv (skip if using your own data)
python src/analysis.py         # runs the full analysis
```

## Using a real dataset
Replace the CSVs in `data/raw/` (e.g. the Olist Brazilian E-commerce dataset on Kaggle) and map columns to:

| File | Columns |
|---|---|
| orders.csv | order_id, customer_id, product_id, order_date, quantity, discount_pct, status, rating |
| customers.csv | customer_id, city, signup_date |
| products.csv | product_id, category, unit_price |

## Tech stack
Python, pandas, NumPy, Matplotlib, Seaborn

## Skills demonstrated
Data cleaning, exploratory data analysis, KPI design, customer segmentation (RFM), data visualisation, translating data into business recommendations.

> Note: the bundled dataset is synthetic, so the numbers illustrate the method rather than real business results.
