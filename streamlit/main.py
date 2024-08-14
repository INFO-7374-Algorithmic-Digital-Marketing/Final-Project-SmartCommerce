import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="E-commerce Platform")

API_URL = "http://localhost:8000"  # Update this with your FastAPI server URL
PROCESSED_DATA_FOLDER_PATH = '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/data_pipeline/data_files/processed/'

@st.cache_data
def load_data():
    df = pd.read_csv(PROCESSED_DATA_FOLDER_PATH + 'orders_full.csv')
    return df

df = load_data()

def authenticate_user(user_id):
    response = requests.post(f"{API_URL}/authenticate", json={"user_id": user_id})
    if response.status_code == 200:
        return response.json()["user_type"]
    else:
        return None

def top_selling_products():
    st.header("Top Selling Products")
    
    product_sales = df.groupby('product_name')['price'].sum().sort_values(ascending=False).head(10)
    
    fig = px.bar(product_sales, x=product_sales.index, y=product_sales.values, title="Top 10 Selling Products")
    st.plotly_chart(fig)
    
    top_product = product_sales.index[0]
    top_product_summary = df[df['product_name'] == top_product]['summary'].iloc[0]
    
    st.subheader("Analysis of Top Product")
    st.write(f"The top-selling product is: {top_product}")
    st.write("Review Summary:")
    st.write(top_product_summary)
    
    st.subheader("AI-Generated Insights")
    st.write("Based on the review summaries, customers appreciate the quality and value of our top-selling products. The positive feedback highlights their durability and functionality, which likely contributes to their popularity.")

def worst_performing_products():
    st.header("Worst Performing Products")
    
    product_sales = df.groupby('product_name')['price'].sum().sort_values().head(10)
    
    fig = px.bar(product_sales, x=product_sales.index, y=product_sales.values, title="10 Worst Performing Products")
    st.plotly_chart(fig)
    
    worst_product = product_sales.index[0]
    worst_product_summary = df[df['product_name'] == worst_product]['summary'].iloc[0]
    
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
    top_seller_products = df[df['seller_id'] == top_seller]['product_name'].value_counts().head()
    
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

st.title("E-commerce Platform")

user_id = st.text_input("Enter your User ID")

if user_id:
    user_type = authenticate_user(user_id)
    
    if user_type == "customer":
        st.sidebar.write("Navigation")
        page = st.sidebar.radio("Go to", ["Recommendation System", "Customer Service"])
        
        if page == "Recommendation System":
            st.header("Recommendation System")
            
            action = st.radio("What would you like to do?", ["Search", "Get Recommendations"])
            
            if action == "Search":
                search_query = st.text_input("Enter your search query")
                if search_query:
                    st.write("Top 10 items for your search:")
                    for i in range(1, 11):
                        st.write(f"{i}. Sample Item {i}")
            
            elif action == "Get Recommendations":
                with st.spinner("Generating recommendations..."):
                    context_aware = requests.post(f"{API_URL}/context_aware_recommendations", json={"user_id": user_id}).json()
                    order_history = requests.post(f"{API_URL}/content_filter_recommendations", json={"user_id": user_id}).json()
                    collaborative = requests.post(f"{API_URL}/collaborative_filtering_recommendations", json={"user_id": user_id}).json()
                    market_basket = requests.post(f"{API_URL}/market_basket_recommendations", json={"user_id": user_id}).json()

                st.subheader("Recommendation Details")

                tabs = st.tabs(["Context-Aware", "Collaborative Filtering", "Order History", "Market Basket"])
                
                def display_product_card(product):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(product['image_url'], use_column_width=True)
                    with col2:
                        st.markdown(f"**[{product['name']}]({product['link']})**")
                        st.write(product['description'][:100] + "..." if len(product['description']) > 100 else product['description'])
                        st.write(f"Price: ${product['avg_price']:.2f}")

                with tabs[0]:
                    st.write("### Context-Aware Recommendations")
                    for product in context_aware:
                        display_product_card(product)
                        st.write("---")

                with tabs[1]:
                    st.write("### Collaborative Filtering Recommendations")
                    for product in collaborative:
                        display_product_card(product)
                        st.write("---")

                with tabs[2]:
                    st.write("### Order History Recommendations")
                    for product in order_history:
                        display_product_card(product)
                        st.write("---")

                with tabs[3]:
                    st.write("### Market Basket Recommendations")
                    for product in market_basket:
                        display_product_card(product)
                        st.write("---")

        elif page == "Customer Service":
            st.header("Customer Service Chatbot")
            user_query = st.text_input("Ask your question here")
            if user_query:
                st.write("Chatbot: Thank you for your question. Our support team will get back to you shortly.")
    
    elif user_type == "seller":
        st.sidebar.write("Navigation")
        page = st.sidebar.radio("Go to", ["Top Selling Products", "Worst Performing Products", "Competitor Analysis", "Customer Targeting", "Supply Chain Optimization"])
        if page == "Top Selling Products":
            top_selling_products()
        elif page == "Worst Performing Products":
            worst_performing_products()
        elif page == "Competitor Analysis":
            competitor_analysis()
        elif page == "Customer Targeting":
            customer_targeting()
        elif page == "Supply Chain Optimization":
            supply_chain_optimization()

    elif user_type is None:
        st.error("User not found. Please enter a valid User ID.")

else:
    st.write("Please enter your User ID to proceed.")