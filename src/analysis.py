"""E-commerce data analysis: cleaning, KPIs, product performance, customer behaviour."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT, FIG = ROOT / "data/raw", ROOT / "data/processed", ROOT / "reports/figures"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid")


def load_and_clean() -> pd.DataFrame:
    orders = pd.read_csv(RAW / "orders.csv", parse_dates=["order_date"])
    customers = pd.read_csv(RAW / "customers.csv", parse_dates=["signup_date"])
    products = pd.read_csv(RAW / "products.csv")

    orders = orders.drop_duplicates("order_id")
    orders["quantity"] = orders["quantity"].fillna(orders["quantity"].median()).astype(int)
    df = orders.merge(products, on="product_id", how="left").merge(customers, on="customer_id", how="left")
    df["revenue"] = df["unit_price"] * df["quantity"] * (1 - df["discount_pct"] / 100)
    df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df.to_csv(OUT / "clean_orders.csv", index=False)
    return df


def kpis(df: pd.DataFrame) -> dict:
    valid = df[df["status"] == "Delivered"]
    return {
        "Total orders": len(df),
        "Net revenue (delivered)": valid["revenue"].sum(),
        "Average order value": valid["revenue"].mean(),
        "Return rate %": (df["status"] == "Returned").mean() * 100,
        "Cancellation rate %": (df["status"] == "Cancelled").mean() * 100,
        "Unique customers": df["customer_id"].nunique(),
        "Repeat customer rate %": (df.groupby("customer_id").size() > 1).mean() * 100,
        "Avg rating": df["rating"].mean(),
    }


def product_performance(df: pd.DataFrame) -> pd.DataFrame:
    valid = df[df["status"] == "Delivered"]
    cat = valid.groupby("category").agg(
        revenue=("revenue", "sum"), units=("quantity", "sum"), avg_rating=("rating", "mean")
    ).sort_values("revenue", ascending=False)
    cat["return_rate_%"] = df.groupby("category")["status"].apply(lambda s: (s == "Returned").mean() * 100)
    return cat


def rfm(df: pd.DataFrame) -> pd.DataFrame:
    """Recency / Frequency / Monetary segmentation of customers."""
    valid = df[df["status"] == "Delivered"]
    snap = valid["order_date"].max() + pd.Timedelta(days=1)
    t = valid.groupby("customer_id").agg(
        recency=("order_date", lambda s: (snap - s.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum"),
    )
    t["R"] = pd.qcut(t["recency"].rank(method="first"), 4, labels=[4, 3, 2, 1]).astype(int)
    t["F"] = pd.qcut(t["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    t["M"] = pd.qcut(t["monetary"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    t["score"] = t[["R", "F", "M"]].sum(axis=1)
    t["segment"] = pd.cut(t["score"], [0, 5, 8, 10, 12], labels=["At risk", "Regular", "Loyal", "Champions"])
    return t


def save(name: str):
    plt.tight_layout()
    plt.savefig(FIG / name, dpi=150)
    plt.close()


def make_charts(df, cat, seg):
    valid = df[df["status"] == "Delivered"]

    ax = valid.groupby("month")["revenue"].sum().plot(figsize=(9, 4), marker="o", title="Monthly revenue")
    ax.set_ylabel("Revenue")
    save("monthly_revenue.png")

    cat["revenue"].plot(kind="barh", figsize=(7, 4), title="Revenue by category").invert_yaxis()
    save("revenue_by_category.png")

    valid.groupby("city")["revenue"].sum().sort_values().plot(kind="barh", figsize=(7, 4), title="Revenue by city")
    save("revenue_by_city.png")

    seg["segment"].value_counts().reindex(["Champions", "Loyal", "Regular", "At risk"]).plot(
        kind="bar", figsize=(6, 4), title="Customer segments (RFM)", rot=0)
    save("rfm_segments.png")

    df.groupby("discount_pct")["status"].apply(lambda s: (s == "Returned").mean() * 100).plot(
        kind="bar", figsize=(6, 4), title="Return rate % by discount level", rot=0)
    save("returns_by_discount.png")


def write_report(k, cat, seg, df):
    valid = df[df["status"] == "Delivered"]
    q4 = valid[valid["order_date"].dt.month >= 10]["revenue"].sum() / valid["revenue"].sum() * 100
    by_seg = seg.groupby("segment", observed=True)["monetary"].sum()
    champ_share = by_seg.get("Champions", 0) / by_seg.sum() * 100
    lines = ["# Key Findings\n", "## KPIs"]
    lines += [f"- **{n}**: {v:,.0f}" if float(v).is_integer() else f"- **{n}**: {v:,.2f}" for n, v in k.items()]
    lines += [
        "\n## Product performance", cat.to_markdown(floatfmt=",.2f"),
        f"\n- Top category by revenue: **{cat.index[0]}**; highest return rate: **{cat['return_rate_%'].idxmax()}**.",
        f"\n## Customer behaviour\n- The Champions segment drives **{champ_share:.1f}%** of revenue.",
        f"- Oct-Dec accounts for **{q4:.1f}%** of revenue (seasonality).",
        "\n## Recommendations",
        "- Build inventory and campaigns ahead of Q4.",
        f"- Investigate quality/description issues in **{cat['return_rate_%'].idxmax()}** to cut returns.",
        "- Run win-back offers for 'At risk' customers; reward 'Champions' with loyalty perks.",
    ]
    (ROOT / "reports/insights.md").write_text("\n".join(lines))


if __name__ == "__main__":
    df = load_and_clean()
    k, cat, seg = kpis(df), product_performance(df), rfm(df)
    make_charts(df, cat, seg)
    write_report(k, cat, seg, df)
    for n, v in k.items():
        print(f"{n:28s}{v:>14,.2f}")
    print("\nReport: reports/insights.md | Charts: reports/figures/")
