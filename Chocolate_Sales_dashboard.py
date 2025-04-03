import pandas as pd
import plotly.express as px
import streamlit as st
# Load data
file_path = "Chocolate_Sales_update.csv"
df = pd.read_csv(file_path)

# Rename columns for clarity
df.rename(columns={
    "sales_person": "Salesperson",
    "country": "Country",
    "product": "Product",
    "date": "Date",
    "amount": "Sales_Amount",
    "boxes_shipped": "Boxes_Shipped",
    "year": "Year",
    "quarter": "Quarter",
    "month_name": "Month",
    "day_name": "Day"
}, inplace=True)

# Color Palette
color_palette = ["#fc6601", "#fa812a", "#8b4000", "#faa602", "#f6a001", "#daa520", "#eb9605", "#883001"]

# Setup
st.set_page_config(layout="wide", page_title="Chocolate Sales Dashboard")

st.markdown("""
<h1 style='color: #2F4858;'>Chocolate Sales Dashboard</h1>
<p style='font-size:16px;'><b>Analyze chocolate sales data across different countries, products, and time periods.</b></p>
""", unsafe_allow_html=True)

# Sidebar Filters
with st.sidebar:
    st.header("Filters")
    countries = sorted(df["Country"].unique().tolist())
    countries.insert(0, "All")
    country = st.multiselect("Country", countries, default=["All"])
    products = sorted(df["Product"].unique().tolist())
    products.insert(0, "All")  
    product = st.multiselect("Product", products, default=["All"])
    quarter = st.selectbox("Quarter", ["All"] + sorted(df["Quarter"].unique().tolist()), index=0)
    month = st.selectbox("Month", ["All"] + sorted(df["Month"].unique().tolist()), index=0)
    price_range = st.slider(
        "Select Price Range",
        int(df["Sales_Amount"].min()),
        int(df["Sales_Amount"].max()),
        (int(df["Sales_Amount"].min()), int(df["Sales_Amount"].max())))


# Apply Filters
filtered_df = df.copy()

# Country Filter
if "All" not in country:
    filtered_df = filtered_df[filtered_df["Country"].isin(country)]

# Product Filter
if "All" not in product:
    filtered_df = filtered_df[filtered_df["Product"].isin(product)]

# Price Range Filter
filtered_df = filtered_df[(filtered_df["Sales_Amount"] >= price_range[0]) & (filtered_df["Sales_Amount"] <= price_range[1])]

# Quarter Filter
if quarter != "All":
    filtered_df = filtered_df[filtered_df["Quarter"] == quarter]

# Month Filter
if month != "All":
    filtered_df = filtered_df[filtered_df["Month"] == month]

# Key Metrics
st.markdown("""
    <style>
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 10px;
    }
    .metric-box {
        border: 2px solid #fc6601;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        width: 100%;
        background-color: #fff8ee;
    }
    </style>
    """, unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
if not filtered_df.empty:
    with col1:
        st.markdown("<div class='metric-box'><b>Total Sales Amount</b><br>${:,.2f}</div>".format(filtered_df['Sales_Amount'].sum()), unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-box'><b>Average Sales per Transaction</b><br>${:,.2f}</div>".format(filtered_df['Sales_Amount'].mean()), unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-box'><b>Total Boxes Shipped</b><br>{:,}</div>".format(filtered_df['Boxes_Shipped'].sum()), unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='metric-box'><b>Average Boxes Shipped</b><br>{:,.2f}</div>".format(filtered_df['Boxes_Shipped'].mean()), unsafe_allow_html=True)
else:
    st.warning("No data available for selected filters.")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Sales Distribution", "Time Analysis", "Product Performance", "Salesperson Performance", "Country Performance", "Correlation Analysis"])

# Sales Distribution
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sales Distribution Overview")
        st.markdown("<h4 style='font-size:18px;'>Summary Statistics</h4>", unsafe_allow_html=True)
        summary_stats = filtered_df[['Sales_Amount', 'Boxes_Shipped']].describe()
        st.dataframe(summary_stats, width=450)
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size:18px;'>Categorical Analysis</h4>", unsafe_allow_html=True)
        object_columns = df.select_dtypes(include=['object']).nunique().reset_index()
        object_columns.columns = ["Column Name", "Unique Values"]
        st.dataframe(object_columns, width=450)
    with col2:
        st.plotly_chart(px.histogram(filtered_df, x="Sales_Amount", title="Sales Amount Distribution", color_discrete_sequence=[color_palette[0]]), use_container_width=True)
        st.plotly_chart(px.histogram(filtered_df, x="Boxes_Shipped", title="Boxes Shipped Distribution", color_discrete_sequence=[color_palette[3]]), use_container_width=True)

# Time Analysis
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sales Amount by Month")
        top_months = filtered_df.groupby("Month")[["Sales_Amount"]].sum().sort_values(by="Sales_Amount", ascending=False).reset_index()
        st.dataframe(top_months, width=500)
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.subheader("Sales Amount by Day of Week")
        top_days = filtered_df.groupby("Day")[["Sales_Amount"]].sum().sort_values(by="Sales_Amount", ascending=False).reset_index()
        st.dataframe(top_days, width=400)
    with col2:
        st.plotly_chart(px.line(top_months, x="Month", y="Sales_Amount", title="Monthly Sales Trends", color_discrete_sequence=[color_palette[2]]).update_traces(mode='lines+markers'), use_container_width=True)
        st.plotly_chart(px.line(top_days, x="Day", y="Sales_Amount", title="Daily Sales Trends", color_discrete_sequence=[color_palette[4]]).update_traces(mode='lines+markers'), use_container_width=True)

# Product Performance
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top Product Sales Performance")
        top_products_sales = filtered_df.groupby("Product")[["Sales_Amount", "Boxes_Shipped"]].sum().sort_values(by="Sales_Amount", ascending=False).head(10).reset_index()
        st.dataframe(top_products_sales, width=450)
        st.plotly_chart(px.bar(top_products_sales, x="Product", y="Sales_Amount", title="Top Products by Sales Amount", color="Product", color_discrete_sequence=color_palette,height =550), use_container_width=True)

    with col2:
        top_products_boxes = filtered_df.groupby("Product")[["Sales_Amount", "Boxes_Shipped"]].sum().sort_values(by="Boxes_Shipped", ascending=False).head(10).reset_index()
        st.plotly_chart(px.pie(top_products_boxes, names="Product", values="Boxes_Shipped", title="Top 10 Products by Boxes Shipped", color_discrete_sequence=color_palette), use_container_width=True)
        st.plotly_chart(px.box(filtered_df, x="Product", y="Boxes_Shipped", title="Boxes Shipped Distribution by Product", color_discrete_sequence=color_palette), use_container_width=True)

# Salesperson Performance
with tab4:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top Salesperson Performance")
        top_salesperson_sales = filtered_df.groupby("Salesperson")[["Sales_Amount", "Boxes_Shipped"]].sum().sort_values(by="Sales_Amount", ascending=False).head(10).reset_index()
        st.dataframe(top_salesperson_sales, width=450)
        st.plotly_chart(px.bar(top_salesperson_sales, x="Salesperson", y="Sales_Amount", title="Top Salespersons by Sales Amount", color="Salesperson", color_discrete_sequence=color_palette ,height =550), use_container_width=True)
    with col2:
        top_salesperson_boxes = filtered_df.groupby("Salesperson")[["Sales_Amount", "Boxes_Shipped"]].sum().sort_values(by="Boxes_Shipped", ascending=False).head(10).reset_index()
        st.plotly_chart(px.pie(top_salesperson_boxes, names="Salesperson", values="Boxes_Shipped", title="Top 10 Salespersons by Boxes Shipped", color_discrete_sequence=color_palette), use_container_width=True)
        st.plotly_chart(px.box(filtered_df, x="Salesperson", y="Boxes_Shipped", title="Boxes Shipped Distribution by Salesperson", color_discrete_sequence=color_palette), use_container_width=True)

# Country Performance
with tab5:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Country-wise Sales Analysis")
        top_country_sales = filtered_df.groupby("Country")[["Sales_Amount", "Boxes_Shipped"]].sum().sort_values(by="Sales_Amount", ascending=False).reset_index()
        st.dataframe(top_country_sales, width=450)
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.plotly_chart(px.bar(top_country_sales, x="Country", y="Sales_Amount", title="Total Sales by Country", color="Country", color_discrete_sequence=color_palette,height =550), use_container_width=True)
    with col2:
        top_country_boxes = filtered_df.groupby("Country")[["Sales_Amount", "Boxes_Shipped"]].sum().sort_values(by="Boxes_Shipped", ascending=False).reset_index()
        st.plotly_chart(px.pie(top_country_boxes, names="Country", values="Boxes_Shipped", title="Boxes Shipped by Country", color_discrete_sequence=color_palette), use_container_width=True)
        st.plotly_chart(px.box(filtered_df, x="Country", y="Boxes_Shipped", title="Boxes Shipped Distribution by Country", color_discrete_sequence=color_palette), use_container_width=True)

# Correlation Analysis
with tab6:
    st.subheader("Correlation Matrix")
    correlation_matrix = filtered_df[["Sales_Amount", "Boxes_Shipped", "Quarter"]].select_dtypes(include=['number']).corr().round(2)
    fig = px.imshow(correlation_matrix, text_auto=True, title="Feature Correlation Heatmap", color_continuous_scale=color_palette, width=800, height=800)
    fig.update_layout(xaxis_title_font=dict(size=16), yaxis_title_font=dict(size=16), title_font=dict(size=20))
    st.plotly_chart(fig, use_container_width=True)
