import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="E-Commerce BI Dashboard", layout="wide")

# ---------- LOAD & MERGE DATA ----------
@st.cache_data
def load_data():
    orders = pd.read_csv('List_of_Orders_clean.csv')
    details = pd.read_csv('Order_Details_clean.csv')
    df = pd.merge(details, orders, on='Order ID', how='left')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Month_Year'] = df['Order Date'].dt.to_period('M').astype(str)
    return df

df = load_data()

# ---------- SIDEBAR FILTERS ----------
st.sidebar.header("Filters")

state_filter = st.sidebar.multiselect("State", options=sorted(df['State'].unique()))
city_filter = st.sidebar.multiselect("City", options=sorted(df['City'].unique()))
category_filter = st.sidebar.multiselect("Category", options=sorted(df['Category'].unique()))
subcat_filter = st.sidebar.multiselect("Sub-Category", options=sorted(df['Sub-Category'].unique()))

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(df['Order Date'].min(), df['Order Date'].max())
)

# Apply filters
filtered_df = df.copy()
if state_filter:
    filtered_df = filtered_df[filtered_df['State'].isin(state_filter)]
if city_filter:
    filtered_df = filtered_df[filtered_df['City'].isin(city_filter)]
if category_filter:
    filtered_df = filtered_df[filtered_df['Category'].isin(category_filter)]
if subcat_filter:
    filtered_df = filtered_df[filtered_df['Sub-Category'].isin(subcat_filter)]
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['Order Date'] >= pd.to_datetime(date_range[0])) &
        (filtered_df['Order Date'] <= pd.to_datetime(date_range[1]))
    ]

# ---------- TITLE ----------
st.title("📊 E-Commerce Business Intelligence Dashboard")

# ---------- KPI CARDS ----------
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Sales", f"₹{filtered_df['Amount'].sum():,.0f}")
col2.metric("Total Profit", f"₹{filtered_df['Profit'].sum():,.0f}")
col3.metric("Total Orders", f"{filtered_df['Order ID'].nunique()}")
col4.metric("Total Quantity", f"{filtered_df['Quantity'].sum()}")
col5.metric("Total Customers", f"{filtered_df['CustomerName'].nunique()}")

st.markdown("---")

# ---------- ROW 1: CATEGORY CHARTS ----------
c1, c2, c3 = st.columns(3)

cat_sales = filtered_df.groupby('Category')['Amount'].sum().reset_index()
fig1 = px.bar(cat_sales, x='Category', y='Amount', title="Sales by Category", color='Category')
c1.plotly_chart(fig1, use_container_width=True)

cat_profit = filtered_df.groupby('Category')['Profit'].sum().reset_index()
fig2 = px.bar(cat_profit, x='Category', y='Profit', title="Profit by Category", color='Category')
c2.plotly_chart(fig2, use_container_width=True)

cat_qty = filtered_df.groupby('Category')['Quantity'].sum().reset_index()
fig3 = px.bar(cat_qty, x='Category', y='Quantity', title="Quantity by Category", color='Category')
c3.plotly_chart(fig3, use_container_width=True)

# ---------- ROW 2: TREND & STATE ----------
c4, c5 = st.columns(2)

monthly = filtered_df.groupby('Month_Year')['Amount'].sum().reset_index()
fig4 = px.line(monthly, x='Month_Year', y='Amount', title="Monthly Sales Trend", markers=True)
c4.plotly_chart(fig4, use_container_width=True)

state_sales = filtered_df.groupby('State')['Amount'].sum().reset_index().sort_values('Amount', ascending=False)
fig5 = px.bar(state_sales, x='State', y='Amount', title="State-wise Sales")
c5.plotly_chart(fig5, use_container_width=True)

# ---------- ROW 3: CITY & TOP CUSTOMERS ----------
c6, c7 = st.columns(2)

city_sales = filtered_df.groupby('City')['Amount'].sum().reset_index().sort_values('Amount', ascending=False).head(10)
fig6 = px.bar(city_sales, x='City', y='Amount', title="Top 10 Cities by Sales")
c6.plotly_chart(fig6, use_container_width=True)

top_cust = filtered_df.groupby('CustomerName')['Amount'].sum().reset_index().sort_values('Amount', ascending=False).head(10)
fig7 = px.bar(top_cust, x='CustomerName', y='Amount', title="Top 10 Customers")
c7.plotly_chart(fig7, use_container_width=True)

# ---------- ROW 4: TOP & LOSS SUB-CATEGORIES ----------
c8, c9 = st.columns(2)

subcat_sales = filtered_df.groupby('Sub-Category')['Amount'].sum().reset_index().sort_values('Amount', ascending=False).head(10)
fig8 = px.bar(subcat_sales, x='Sub-Category', y='Amount', title="Top 10 Sub-Categories by Sales")
c8.plotly_chart(fig8, use_container_width=True)

subcat_profit = filtered_df.groupby('Sub-Category')['Profit'].sum().reset_index().sort_values('Profit')
loss_subcats = subcat_profit[subcat_profit['Profit'] < 0]
fig9 = px.bar(loss_subcats, x='Sub-Category', y='Profit', title="Loss-Making Sub-Categories", color='Profit')
c9.plotly_chart(fig9, use_container_width=True)

# ---------- BUSINESS INSIGHTS ----------
st.markdown("---")
st.subheader("📌 Business Insights")

best_cat = cat_sales.loc[cat_sales['Amount'].idxmax(), 'Category']
worst_cat = cat_sales.loc[cat_sales['Amount'].idxmin(), 'Category']
most_profit_cat = cat_profit.loc[cat_profit['Profit'].idxmax(), 'Category']

insight_col1, insight_col2, insight_col3 = st.columns(3)
insight_col1.info(f"**Best Category (Sales):** {best_cat}")
insight_col2.warning(f"**Weakest Category (Sales):** {worst_cat}")
insight_col3.success(f"**Most Profitable Category:** {most_profit_cat}")

if len(loss_subcats) > 0:
    st.error(f"**Loss-Making Sub-Categories:** {', '.join(loss_subcats['Sub-Category'].tolist())}")
else:
    st.success("No loss-making sub-categories in current filter selection.")