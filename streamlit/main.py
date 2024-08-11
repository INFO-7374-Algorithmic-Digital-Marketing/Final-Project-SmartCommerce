import streamlit as st
import requests
import json

API_URL = "http://localhost:8000"  # Update this with your FastAPI server URL

def authenticate_user(user_id):
    response = requests.post(f"{API_URL}/authenticate", json={"user_id": user_id})
    if response.status_code == 200:
        return response.json()["user_type"]
    else:
        return None

st.set_page_config(layout="wide", page_title="E-commerce Platform")

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
                        st.progress(min(product['avg_sentiment_score'], 1.0))
                        st.write(f"Sentiment Score: {product['avg_sentiment_score']:.2f}")

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
        page = st.sidebar.radio("Go to", ["Seller Dashboard"])
        
        if page == "Seller Dashboard":
            st.header("Seller Dashboard")
            st.write("Welcome to your seller dashboard!")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Sales Overview")
                st.line_chart({"Sales": [100, 120, 80, 150, 200, 180]})
            with col2:
                st.subheader("Top Products")
                st.bar_chart({"Product A": 300, "Product B": 250, "Product C": 200, "Product D": 150})

    elif user_type is None:
        st.error("User not found. Please enter a valid User ID.")

else:
    st.write("Please enter your User ID to proceed.")