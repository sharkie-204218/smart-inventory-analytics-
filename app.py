
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Smart Inventory Analytics", layout="wide")

st.title("📦 Smart Inventory Analytics")
st.caption("Inventory & Supply Chain Management Dashboard")

# Simulated business data
data = pd.DataFrame({
    "Product": ["Laptop", "Monitor", "Keyboard", "Mouse", "Printer", "Desk", "Chair", "Tablet"],
    "Category": ["Electronics", "Electronics", "Accessories", "Accessories",
                 "Electronics", "Furniture", "Furniture", "Electronics"],
    "Stock": [120, 45, 200, 320, 18, 35, 12, 75],
    "Unit Price": [4500, 1200, 150, 80, 1800, 900, 650, 2300],
    "Reorder Level": [30, 40, 100, 100, 25, 20, 20, 30]
})

st.sidebar.header("Data Management")
uploaded_file = st.sidebar.file_uploader(
    "Upload inventory data (CSV or Excel)",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)
        required = {"Product", "Category", "Stock", "Unit Price", "Reorder Level"}
        if not required.issubset(data.columns):
            st.error("Missing required columns: " + ", ".join(sorted(required - set(data.columns))))
            st.stop()
        for col in ["Stock", "Unit Price", "Reorder Level"]:
            data[col] = pd.to_numeric(data[col], errors="raise")
        if data[["Stock", "Unit Price", "Reorder Level"]].isna().any().any():
            st.error("Numeric columns cannot contain missing values.")
            st.stop()
    except Exception as e:
        st.error(f"Unable to read inventory file: {e}")
        st.stop()

data["Inventory Value"] = data["Stock"] * data["Unit Price"]
low_stock = data[data["Stock"] < data["Reorder Level"]]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Units", f"{data['Stock'].sum():,.0f}")
col2.metric("Inventory Value (CNY)", f"¥{data['Inventory Value'].sum():,.0f}")
col3.metric("Products", len(data))
col4.metric("Low Stock Alerts", len(low_stock))

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Inventory by Category")
    category_data = data.groupby("Category", as_index=False)["Inventory Value"].sum()
    fig = px.pie(category_data, names="Category", values="Inventory Value", hole=0.45)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Stock Levels by Product")
    fig = px.bar(data, x="Product", y="Stock", color="Category")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("⚠️ Low Stock Alerts")
if low_stock.empty:
    st.success("All products are above their reorder levels.")
else:
    st.dataframe(low_stock, use_container_width=True)

st.subheader("Inventory Details")
st.dataframe(data, use_container_width=True)

st.download_button(
    "Download Inventory Report",
    data=data.to_csv(index=False).encode("utf-8-sig"),
    file_name="inventory_report.csv",
    mime="text/csv"
)

st.caption("Portfolio demo using simulated data. Currency assumed to be CNY.")
