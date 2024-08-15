import streamlit as st
import pandas as pd
import plotly.express as px

if "user_type" not in st.session_state or st.session_state.user_type != "seller":
    st.switch_page("pages/1_Login.py")

PROCESSED_DATA_FOLDER_PATH = '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/data_pipeline/data_files/processed/'

@st.cache_data
def load_data():
    df = pd.read_csv(PROCESSED_DATA_FOLDER_PATH + 'orders_full.csv')
    return df

df = load_data()

def top_selling_products():
    st.header("Top Selling Products")
    
    product_sales = df.groupby('title')['price'].sum().sort_values(ascending=False).head(10)
    
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
    
    product_sales = df.groupby('title')['price'].sum().sort_values().head(10)
    
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
    
    seller_sales = df.groupby('seller_id')['price'].sum().sort_values(ascending=False).head(5)
    
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
    
    state_sales = df.groupby('customer_state')['price'].sum().sort_values(ascending=False).head(5)
    
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


st.sidebar.title("Seller Dashboard")
page = st.sidebar.radio("Go to", ["Top Selling Products", "Worst Performing Products", "Competitor Analysis", "Customer Targeting", "Supply Chain Optimization"])

if page == "Top Selling Products":
    pass
    # Your existing top_selling_products() function code here
elif page == "Worst Performing Products":
    pass
    # Your existing worst_performing_products() function code here
elif page == "Competitor Analysis":
    pass
    # Your existing competitor_analysis() function code here
elif page == "Customer Targeting":
    pass
    # Your existing customer_targeting() function code here
elif page == "Supply Chain Optimization":
    pass
    # Your existing supply_chain_optimization() function code here