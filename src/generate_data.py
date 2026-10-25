"""Generate a realistic synthetic e-commerce dataset (orders, customers, products).

To use a real dataset (e.g. Olist on Kaggle), place CSVs with the same columns
in data/raw/ and skip this script.
"""
from pathlib import Path
import numpy as np
import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(42)

N_CUSTOMERS, N_PRODUCTS, N_ORDERS = 3000, 120, 15000

categories = {
    "Electronics": (80, 600), "Fashion": (15, 120), "Home & Kitchen": (20, 200),
    "Beauty": (8, 70), "Books": (5, 40), "Sports": (15, 250), "Toys": (8, 80),
}
cities = ["Hyderabad", "Bengaluru", "Mumbai", "Delhi", "Chennai", "Guntur", "Pune", "Kolkata"]

products = pd.DataFrame({
    "product_id": [f"P{i:04d}" for i in range(N_PRODUCTS)],
    "category": rng.choice(list(categories), N_PRODUCTS, p=[.18, .22, .16, .12, .10, .12, .10]),
})
products["unit_price"] = [round(rng.uniform(*categories[c]), 2) for c in products["category"]]

customers = pd.DataFrame({
    "customer_id": [f"C{i:05d}" for i in range(N_CUSTOMERS)],
    "city": rng.choice(cities, N_CUSTOMERS),
    "signup_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 700, N_CUSTOMERS), unit="D"),
})

# Skewed activity (some customers order far more) and Q4 seasonality
weights = rng.pareto(2.0, N_CUSTOMERS) + 1
weights /= weights.sum()
dates = pd.date_range("2023-01-01", "2024-12-31")
season = np.array([1.6 if d.month in (10, 11, 12) else 1.0 for d in dates])
season /= season.sum()

orders = pd.DataFrame({
    "order_id": [f"O{i:06d}" for i in range(N_ORDERS)],
    "customer_id": rng.choice(customers["customer_id"], N_ORDERS, p=weights),
    "product_id": rng.choice(products["product_id"], N_ORDERS),
    "order_date": rng.choice(dates, N_ORDERS, p=season),
    "quantity": rng.choice([1, 2, 3, 4], N_ORDERS, p=[.7, .2, .07, .03]).astype(float),
    "discount_pct": rng.choice([0, 5, 10, 20], N_ORDERS, p=[.55, .2, .15, .1]),
    "status": rng.choice(["Delivered", "Returned", "Cancelled"], N_ORDERS, p=[.88, .07, .05]),
    "rating": rng.choice([1, 2, 3, 4, 5, np.nan], N_ORDERS, p=[.04, .06, .15, .3, .35, .10]),
})

# Inject some mess so the cleaning step has real work to do
orders.loc[rng.choice(N_ORDERS, 60, replace=False), "quantity"] = np.nan
orders = pd.concat([orders, orders.sample(40, random_state=1)])  # duplicate rows

orders.to_csv(RAW / "orders.csv", index=False)
customers.to_csv(RAW / "customers.csv", index=False)
products.to_csv(RAW / "products.csv", index=False)
print(f"Wrote {len(orders)} orders, {len(customers)} customers, {len(products)} products to {RAW}")
