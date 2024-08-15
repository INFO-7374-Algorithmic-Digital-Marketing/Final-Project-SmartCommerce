import streamlit as st
import pandas as pd
import plotly.express as px
# Create a logout button at the top right
col1, col2 = st.columns([8, 1])
with col2:
    if st.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()  # Refresh the page to apply changes

if "user_type" not in st.session_state or st.session_state.user_type != "seller":
    st.switch_page("pages/1_Login.py")

PROCESSED_DATA_FOLDER_PATH = '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/data_pipeline/data_files/processed/'

@st.cache_data
def load_data():
    df = pd.read_csv(PROCESSED_DATA_FOLDER_PATH + 'orders_full.csv')
    return df

df = load_data()

def create_metric_card(title, chart, insight, details_func):
    with st.expander(title, expanded=True):
        col1, col2 = st.columns([3, 2])
        with col1:
            st.plotly_chart(chart, use_container_width=True)
        with col2:
            st.subheader("AI Insight")
            st.write(insight)
        if st.button(f"View Details for {title}"):
            details_func()

def seller_dashboard():
    st.title("Seller Dashboard")
    st.write("Welcome to your comprehensive seller analytics dashboard.")

    # Top Selling Products
    product_sales = df.groupby('title')['target_price'].sum().sort_values(ascending=False).head(10)
    top_chart = px.bar(product_sales, x=product_sales.index, y=product_sales.values, title="Top 10 Selling Products")
    top_insight = "Your best-selling product is driving significant revenue. Consider expanding its product line or running promotions to boost sales further."
    create_metric_card("Top Selling Products", top_chart, top_insight, top_selling_products)

    # Worst Performing Products
    product_sales_worst = df.groupby('title')['target_price'].sum().sort_values().head(10)
    worst_chart = px.bar(product_sales_worst, x=product_sales_worst.index, y=product_sales_worst.values, title="10 Worst Performing Products")
    worst_insight = "Your lowest-performing product may need quality improvements or a pricing strategy review to boost its performance."
    create_metric_card("Worst Performing Products", worst_chart, worst_insight, worst_performing_products)

    # Competitor Analysis
    seller_sales = df.groupby('seller_id')['target_price'].sum().sort_values(ascending=False).head(5)
    competitor_chart = px.bar(seller_sales, x=seller_sales.index, y=seller_sales.values, title="Top 5 Sellers")
    competitor_insight = "The top competitor is outperforming in key product categories. Consider diversifying your product range to compete effectively."
    create_metric_card("Competitor Analysis", competitor_chart, competitor_insight, competitor_analysis)

    # Customer Targeting
    persona_counts = df['persona_column'].value_counts()
    customer_chart = px.pie(values=persona_counts.values, names=persona_counts.index, title="Customer Personas")
    customer_insight = f"The '{persona_counts.index[0]}' persona represents your largest customer segment. Tailor your marketing efforts to this group."
    create_metric_card("Customer Targeting", customer_chart, customer_insight, customer_targeting)

    # Supply Chain Optimization
    customer_locations = df['customer_zip_code_prefix'].value_counts().head(10)
    supply_chart = px.bar(customer_locations, x=customer_locations.index, y=customer_locations.values, title="Top 10 Customer Zip Code Prefixes")
    supply_insight = f"Consider establishing a distribution center near zip code prefix {customer_locations.index[0]} to serve a large customer base efficiently."
    create_metric_card("Supply Chain Optimization", supply_chart, supply_insight, supply_chain_optimization)

# (Keep your existing function definitions for top_selling_products, worst_performing_products, etc.)
def top_selling_products():
    st.header("Top Selling Products")
    
    product_sales = df.groupby('title')['target_price'].sum().sort_values(ascending=False).head(10)
    
    fig = px.bar(product_sales, x=product_sales.index, y=product_sales.values, title="Top 10 Selling Products")
    st.plotly_chart(fig)
    
    top_product = product_sales.index[0]
    top_product_summary = df[df['title'] == top_product]['summary'].iloc[0]
    
    st.subheader("Analysis of Top Product")
    st.write(f"The top-selling product is: {top_product}")
    st.write("Review Summary:")
    st.write(top_product_summary)
    
    st.subheader("AI-Generated Insights")
    st.write("Based on the review summaries, customers appreciate the quality and value of our top-selling products. The positive feedback highlights their durability and functionality, which likely contributes to their popularity.")

def worst_performing_products():
    st.header("Worst Performing Products")
    
    product_sales = df.groupby('title')['target_price'].sum().sort_values().head(10)
    
    fig = px.bar(product_sales, x=product_sales.index, y=product_sales.values, title="10 Worst Performing Products")
    st.plotly_chart(fig)
    
    worst_product = product_sales.index[0]
    worst_product_summary = df[df['title'] == worst_product]['summary'].iloc[0]
    
    st.subheader("Analysis of Worst Performing Product")
    st.write(f"The worst-performing product is: {worst_product}")
    st.write("Review Summary:")
    st.write(worst_product_summary)
    
    st.subheader("AI-Generated Insights and Recommendations")
    st.write("Based on the review summaries, customers have expressed concerns about the product's quality and value for money. To improve performance, consider:")
    st.write("1. Enhancing product quality based on specific customer feedback")
    st.write("2. Reviewing pricing strategy to ensure it aligns with perceived value")
    st.write("3. Improving product descriptions to set accurate expectations")
    st.write("4. Offering better customer support for these products")

def competitor_analysis():
    st.header("Competitor Analysis")
    
    seller_sales = df.groupby('seller_id')['target_price'].sum().sort_values(ascending=False).head(5)
    
    fig = px.bar(seller_sales, x=seller_sales.index, y=seller_sales.values, title="Top 5 Sellers")
    st.plotly_chart(fig)
    
    top_seller = seller_sales.index[0]
    top_seller_products = df[df['seller_id'] == top_seller]['title'].value_counts().head()
    
    st.subheader("Top Seller's Best-Selling Products")
    st.write(top_seller_products)
    
    st.subheader("AI-Generated Competitor Insights")
    st.write("Based on the analysis of top-selling products from leading competitors:")
    st.write("1. Competitors focus on high-demand product categories")
    st.write("2. They maintain competitive pricing while ensuring product quality")
    st.write("3. Top sellers have a diverse product range to cater to various customer needs")
    st.write("4. Effective marketing and customer engagement strategies contribute to their success")

def customer_targeting():
    st.header("Customer Targeting")
    
    persona_counts = df['persona_column'].value_counts()
    
    fig = px.pie(values=persona_counts.values, names=persona_counts.index, title="Customer Personas")
    st.plotly_chart(fig)
    
    state_sales = df.groupby('customer_state')['target_price'].sum().sort_values(ascending=False).head(5)
    
    fig = px.bar(state_sales, x=state_sales.index, y=state_sales.values, title="Top 5 States by Sales")
    st.plotly_chart(fig)
    
    st.subheader("AI-Generated Targeting Recommendations")
    st.write("Based on the customer persona and regional sales analysis:")
    st.write(f"1. Focus on the '{persona_counts.index[0]}' persona for targeted marketing campaigns")
    st.write(f"2. Prioritize marketing efforts in {state_sales.index[0]} and {state_sales.index[1]} states")
    st.write("3. Develop seasonal promotions tailored to each region's trends")
    st.write("4. Create personalized email campaigns for each customer persona")

def supply_chain_optimization():
    st.header("Supply Chain Optimization")
    
    customer_locations = df['customer_zip_code_prefix'].value_counts().head(10)
    
    fig = px.bar(customer_locations, x=customer_locations.index, y=customer_locations.values, title="Top 10 Customer Zip Code Prefixes")
    st.plotly_chart(fig)
    
    seller_locations = df['seller_zip_code_prefix'].value_counts().head(10)
    
    fig = px.bar(seller_locations, x=seller_locations.index, y=seller_locations.values, title="Top 10 Seller Zip Code Prefixes")
    st.plotly_chart(fig)
    
    st.subheader("AI-Generated Supply Chain Recommendations")
    st.write("Based on the analysis of customer and seller locations:")
    st.write(f"1. Consider establishing a distribution center near zip code prefix {customer_locations.index[0]} to serve a large customer base")
    st.write(f"2. Explore partnerships with sellers in {seller_locations.index[0]} to optimize supply chain efficiency")
    st.write("3. Investigate potential gaps between high-demand customer areas and current seller locations")
    st.write("4. Evaluate the possibility of expanding seller network in underserved high-demand areas")

seller_dashboard()