import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Smart Inventory Analytics V2", page_icon="📦", layout="wide")

REQUIRED = ["Product", "Category", "Stock", "Unit Price", "Reorder Level"]

@st.cache_data
def sample_inventory():
    return pd.DataFrame({
        "Product": ["Laptop", "Monitor", "Keyboard", "Mouse", "Printer", "Desk", "Chair", "Tablet"],
        "Category": ["Electronics", "Electronics", "Accessories", "Accessories", "Electronics", "Furniture", "Furniture", "Electronics"],
        "Stock": [120, 45, 200, 320, 18, 35, 12, 75],
        "Unit Price": [4500, 1200, 150, 80, 1800, 900, 650, 2300],
        "Reorder Level": [30, 40, 100, 100, 25, 20, 20, 30],
    })

@st.cache_data
def sample_transactions():
    months = pd.date_range("2025-12-01", periods=12, freq="MS")
    purchases = [180, 195, 210, 190, 240, 260, 230, 275, 290, 265, 310, 325]
    sales = [155, 175, 205, 215, 220, 245, 250, 255, 280, 295, 300, 315]
    return pd.DataFrame({"Month": months, "Purchases": purchases, "Sales": sales})

def read_file(upload):
    return pd.read_csv(upload) if upload.name.lower().endswith(".csv") else pd.read_excel(upload)

def validate_inventory(frame):
    frame = frame.copy()
    missing = sorted(set(REQUIRED) - set(frame.columns))
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))
    if frame.empty:
        raise ValueError("Inventory file contains no rows.")
    for column in ["Stock", "Unit Price", "Reorder Level"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        if frame[column].isna().any() or (frame[column] < 0).any():
            raise ValueError(f"{column} must contain non-negative numbers without missing values.")
    if frame[["Product", "Category"]].isna().any().any():
        raise ValueError("Product and Category cannot be empty.")
    frame["Product"] = frame["Product"].astype(str)
    frame["Category"] = frame["Category"].astype(str)
    if frame[["Product", "Category"]].apply(lambda col: col.str.strip().eq("")).any().any():
        raise ValueError("Product and Category cannot be blank.")
    return frame

def validate_transactions(frame):
    required = {"Month", "Purchases", "Sales"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError("Missing transaction columns: " + ", ".join(missing))
    if frame.empty:
        raise ValueError("Transaction file contains no rows.")
    frame = frame.copy()
    frame["Month"] = pd.to_datetime(frame["Month"], errors="raise")
    if frame["Month"].isna().any():
        raise ValueError("Month cannot be empty.")
    for column in ["Purchases", "Sales"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        if frame[column].isna().any() or (frame[column] < 0).any():
            raise ValueError(f"{column} must contain non-negative numbers without missing values.")
    return frame.groupby("Month", as_index=False)[["Purchases", "Sales"]].sum().sort_values("Month")

st.title("📦 Smart Inventory Analytics")
st.caption("V2.0 · Inventory & Supply Chain Intelligence · Demonstration data")

with st.sidebar:
    st.header("Data Management")
    inventory_file = st.file_uploader("Inventory CSV / Excel", type=["csv", "xlsx"], key="inventory")
    transactions_file = st.file_uploader("Monthly transactions CSV / Excel (optional)", type=["csv", "xlsx"], key="transactions")
    st.caption("Inventory columns: Product, Category, Stock, Unit Price, Reorder Level")
    st.caption("Transaction columns: Month, Purchases, Sales")
    st.info("Unit Price is used as an estimated replenishment unit cost for demonstration only.")

try:
    inventory = validate_inventory(read_file(inventory_file) if inventory_file else sample_inventory())
    transactions = validate_transactions(read_file(transactions_file) if transactions_file else sample_transactions())
except Exception as exc:
    st.error(f"Data validation error: {exc}")
    st.stop()

inventory["Inventory Value"] = inventory["Stock"] * inventory["Unit Price"]
inventory["Stock Status"] = inventory.apply(
    lambda row: "Low Stock" if row["Stock"] < row["Reorder Level"] else "Healthy", axis=1
)
inventory["Suggested Reorder Qty"] = (inventory["Reorder Level"] - inventory["Stock"]).clip(lower=0)
inventory["Estimated Reorder Cost"] = inventory["Suggested Reorder Qty"] * inventory["Unit Price"]

with st.sidebar:
    st.divider()
    st.header("Filters")
    categories = sorted(inventory["Category"].unique().tolist())
    selected_categories = st.multiselect("Product categories", categories, default=categories)
    status = st.selectbox("Stock status", ["All", "Low Stock", "Healthy"])

filtered = inventory[inventory["Category"].isin(selected_categories)].copy()
if status != "All":
    filtered = filtered[filtered["Stock Status"] == status]

st.subheader("Inventory Overview")
a, b, c, d = st.columns(4)
a.metric("Total Units", f"{filtered['Stock'].sum():,.0f}")
b.metric("Inventory Value (CNY)", f"¥{filtered['Inventory Value'].sum():,.0f}")
c.metric("Products", f"{len(filtered):,}")
d.metric("Low Stock Alerts", f"{(filtered['Stock Status'] == 'Low Stock').sum():,}")
st.caption("Inventory metrics reflect the current category and stock-status filters.")

if filtered.empty:
    st.warning("No inventory products match the selected filters.")
else:
    left, right = st.columns(2)
    with left:
        st.subheader("Inventory Value by Category")
        category_values = filtered.groupby("Category", as_index=False)["Inventory Value"].sum()
        fig = px.pie(category_values, names="Category", values="Inventory Value", hole=0.5)
        st.plotly_chart(fig, width="stretch")
    with right:
        st.subheader("Stock by Product")
        fig = px.bar(filtered, x="Product", y="Stock", color="Stock Status", barmode="group")
        st.plotly_chart(fig, width="stretch")

st.divider()
st.subheader("Purchasing & Sales Trends")
st.caption("Transaction trends use the separately uploaded monthly file, or simulated 12-month data; inventory filters do not affect this chart.")
trends = transactions.melt(id_vars="Month", value_vars=["Purchases", "Sales"], var_name="Flow", value_name="Units")
fig = px.line(trends, x="Month", y="Units", color="Flow", markers=True, title="Monthly Purchasing vs Sales (Units)")
st.plotly_chart(fig, width="stretch")
p1, p2, p3 = st.columns(3)
p1.metric("Total Purchased", f"{transactions['Purchases'].sum():,.0f}")
p2.metric("Total Sold", f"{transactions['Sales'].sum():,.0f}")
p3.metric("Net Inflow (Units)", f"{(transactions['Purchases'].sum() - transactions['Sales'].sum()):,.0f}")
st.caption("Net inflow is purchases minus sales for the transaction period, not the current stock balance.")

st.divider()
st.subheader("Rule-based Replenishment Recommendations")
st.caption("Suggested reorder quantity = max(reorder level − current stock, 0). This is a threshold rule, not an AI forecast.")
reorders = filtered[filtered["Suggested Reorder Qty"] > 0].copy()
r1, r2 = st.columns(2)
r1.metric("Products to Reorder", len(reorders))
r2.metric("Estimated Replenishment Budget", f"¥{reorders['Estimated Reorder Cost'].sum():,.0f}")
if reorders.empty:
    st.success("No products require replenishment under the current filters.")
else:
    st.dataframe(
        reorders[["Product", "Category", "Stock", "Reorder Level", "Suggested Reorder Qty", "Estimated Reorder Cost"]],
        width="stretch", hide_index=True
    )

st.subheader("Inventory Details")
st.dataframe(filtered, width="stretch", hide_index=True)
st.download_button(
    "Download Filtered Inventory Report (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8-sig"),
    file_name="inventory_analysis_v2.csv",
    mime="text/csv"
)
st.download_button(
    "Download Replenishment Plan (CSV)",
    data=reorders.to_csv(index=False).encode("utf-8-sig"),
    file_name="replenishment_plan_v2.csv",
    mime="text/csv"
)
st.caption("Portfolio project · All built-in datasets are simulated · Monetary values are in CNY")


