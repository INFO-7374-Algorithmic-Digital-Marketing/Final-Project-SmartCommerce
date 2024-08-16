# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import requests

# # Create a logout button at the top right
# col1, col2 = st.columns([8, 1])
# with col2:
#     if st.button("Logout"):
#         for key in st.session_state.keys():
#             del st.session_state[key]
#         st.rerun()  # Refresh the page to apply changes

# if "user_type" not in st.session_state or st.session_state.user_type != "seller":
#     st.switch_page("pages/1_Login.py")

# API_URL = "http://localhost:8000"

# def top_selling_products():
#     data = requests.get(f"{API_URL}/top_selling_products", json={"user_id": st.session_state.user_id}).json()
#     print("Data:", data)

#     with st.expander("Top Selling Products", expanded=True):
#         col1, col2 = st.columns([3, 2])
#         with col1:
#             product_sales = pd.Series(data['product_sales'])
#             fig = px.bar(product_sales, x=product_sales.index, y=product_sales.values, title="Top 10 Selling Products")
#             st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             st.subheader("Brief AI Insight")
#             st.write(data["brief_ai_insight"])
        
#         if st.button("View Details for Top Selling Products"):
#             st.header("Top Selling Products")
            
#             product_sales = pd.Series(data['product_sales'])
#             fig = px.bar(product_sales, x=product_sales.index, y=product_sales.values, title="Top 10 Selling Products")
#             st.plotly_chart(fig)
            
#             st.subheader("Analysis of Top Product")
#             st.write(f"The top-selling product is: {data['top_product']}")
#             st.write("Review Summary:")
#             st.write(data['top_product_summary'])
            
#             st.subheader("AI-Generated Insightsss")
#             st.write(data['detailed_insights'])


# def worst_performing_products():
#     data = requests.get(f"{API_URL}/worst_performing_products", json={"user_id": st.session_state.user_id}).json()
#     print("Data:", data)

#     with st.expander("Worst Performing Products", expanded=True):
#         col1, col2 = st.columns([3, 2])
#         with col1:
#             product_sales = pd.Series(data['product_sales'])
#             fig = px.bar(product_sales, x=product_sales.index, y=product_sales.values, title="10 Worst Performing Products")
#             st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             st.subheader("AI Insight")
#             st.write(data["brief_ai_insight"])
        
#         if st.button("View Details for Worst Performing Products"):
#             st.header("Worst Performing Products")
            
#             product_sales = pd.Series(data['product_sales'])
#             fig = px.bar(product_sales, x=product_sales.index, y=product_sales.values, title="10 Worst Performing Products")
#             st.plotly_chart(fig)
            
#             st.subheader("Analysis of Worst Performing Product")
#             st.write(f"The worst-performing product is: {data['worst_product']}")
#             st.write("Review Summary:")
#             st.write(data['worst_product_summary'])
            
#             st.subheader("AI-Generated Insights and Recommendations")
#             st.write(data['detailed_insights'])

# def competitor_analysis():
#     data = requests.get(f"{API_URL}/competitor_analysis", json={"user_id": st.session_state.user_id}).json()
#     print("Data:", data)

#     with st.expander("Competitor Analysis", expanded=True):
#         col1, col2 = st.columns([3, 2])
#         with col1:
#             seller_sales = pd.Series(data['seller_sales'])
#             fig = px.bar(seller_sales, x=seller_sales.index, y=seller_sales.values, title="Top 5 Sellers")
#             st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             st.subheader("AI Insight")
#             st.write(data["brief_ai_insight"])
        
#         if st.button("View Details for Competitor Analysis"):
#             st.header("Competitor Analysis")
            
#             seller_sales = pd.Series(data['seller_sales'])
#             fig = px.bar(seller_sales, x=seller_sales.index, y=seller_sales.values, title="Top 5 Sellers")
#             st.plotly_chart(fig)
            
#             st.subheader("Top Seller's Best-Selling Products")
#             st.write(data['top_seller_products'])
            
#             st.subheader("AI-Generated Competitor Insights")
#             st.write(data['detailed_insights'])


# def customer_targeting():
#     data = requests.get(f"{API_URL}/customer_targeting", json={"user_id": st.session_state.user_id}).json()
#     print("Data:", data)

#     with st.expander("Customer Targeting", expanded=True):
#         col1, col2 = st.columns([3, 2])
#         with col1:
#             persona_counts = pd.Series(data['persona_counts'])
#             fig = px.pie(values=persona_counts.values, names=persona_counts.index, title="Customer Personas")
#             st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             st.subheader("AI Insight")
#             st.write(data["brief_ai_insight"])
        
#         if st.button("View Details for Customer Targeting"):
#             st.header("Customer Targeting")
            
#             persona_counts = pd.Series(data['persona_counts'])
#             fig = px.pie(values=persona_counts.values, names=persona_counts.index, title="Customer Personas")
#             st.plotly_chart(fig)
            
#             state_sales = pd.Series(data['state_sales'])
#             fig = px.bar(state_sales, x=state_sales.index, y=state_sales.values, title="Top 5 States by Sales")
#             st.plotly_chart(fig)
            
#             st.subheader("AI-Generated Targeting Recommendations")
#             st.write(data['detailed_insights'])


# import requests

# def supply_chain_optimization():
#     try:
#         response = requests.get(f"{API_URL}/supply_chain_optimization", json={"user_id": st.session_state.user_id})
#         response.raise_for_status()  # Raise an error for bad status codes
#         data = response.json()  # Attempt to parse JSON response
#     except requests.exceptions.RequestException as e:
#         st.error(f"Failed to retrieve data: {e}")
#         return
#     except ValueError as e:
#         st.error(f"Failed to parse JSON response: {e}")
#         return
    
#     print("Data:", data)
    
#     with st.expander("Supply Chain Optimization", expanded=True):
#         col1, col2 = st.columns([3, 2])
#         with col1:
#             customer_locations = pd.Series(data['customer_locations'])
#             fig = px.bar(customer_locations, x=customer_locations.index, y=customer_locations.values, title="Top 10 Customer Zip Code Prefixes")
#             st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             st.subheader("AI Insight")
#             st.write(data["brief_ai_insight"])
        
#         if st.button("View Details for Supply Chain Optimization"):
#             st.header("Supply Chain Optimization")
            
#             customer_locations = pd.Series(data['customer_locations'])
#             fig = px.bar(customer_locations, x=customer_locations.index, y=customer_locations.values, title="Top 10 Customer Zip Code Prefixes")
#             st.plotly_chart(fig)
            
#             seller_locations = pd.Series(data['seller_locations'])
#             fig = px.bar(seller_locations, x=seller_locations.index, y=seller_locations.values, title="Top 10 Seller Zip Code Prefixes")
#             st.plotly_chart(fig)
            
#             st.subheader("AI-Generated Supply Chain Recommendations")
#             st.write(data['detailed_insights'])


# def seller_dashboard():
#     st.title("Seller Dashboard")
#     st.write("Welcome to your comprehensive seller analytics dashboard.")
    
#     top_selling_products()
#     worst_performing_products()
#     competitor_analysis()
#     customer_targeting()
#     supply_chain_optimization()

# seller_dashboard()
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Create a logout button at the top right
col1, col2 = st.columns([8, 1])
with col2:
    if st.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()  # Refresh the page to apply changes

if "user_type" not in st.session_state or st.session_state.user_type != "seller":
    st.switch_page("pages/1_Login.py")

API_URL = "http://localhost:8000"

@st.cache_data
def fetch_data(endpoint, user_id):
    response = requests.post(f"{API_URL}/{endpoint}", json={"user_id": user_id})
    return response.json()

def top_selling_products():
    data = fetch_data("top_selling_products", st.session_state.user_id)
    print("Data:", data)

    with st.expander("Top Selling Products", expanded=True):
        col1, col2 = st.columns([3, 2])
        with col1:
            product_sales = pd.Series(data['product_sales'])
            fig = px.bar(product_sales, x=product_sales.index, y=product_sales.values, title="Top 10 Selling Products")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Brief AI Insight")
            st.write(data["brief_ai_insight"])
        
        if st.button("View Details for Top Selling Products"):
            st.header("Top Selling Products")
            
            product_sales = pd.Series(data['product_sales'])
            fig = px.bar(product_sales, x=product_sales.index, y=product_sales.values, title="Top 10 Selling Products")
            st.plotly_chart(fig)
            
            st.subheader("Analysis of Top Product")
            st.write(f"The top-selling product is: {data['top_product']}")
            st.write("Review Summary:")
            st.write(data['top_product_summary'])
            
            st.subheader("AI-Generated Insights")
            st.write(data['detailed_insights'])


def worst_performing_products():
    data = fetch_data("worst_performing_products", st.session_state.user_id)
    print("Data:", data)

    with st.expander("Worst Performing Products", expanded=True):
        col1, col2 = st.columns([3, 2])
        with col1:
            product_sales = pd.Series(data['product_sales'])
            fig = px.bar(product_sales, x=product_sales.index, y=product_sales.values, title="10 Worst Performing Products")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("AI Insight")
            st.write(data["brief_ai_insight"])
        
        if st.button("View Details for Worst Performing Products"):
            st.header("Worst Performing Products")
            
            product_sales = pd.Series(data['product_sales'])
            fig = px.bar(product_sales, x=product_sales.index, y=product_sales.values, title="10 Worst Performing Products")
            st.plotly_chart(fig)
            
            st.subheader("Analysis of Worst Performing Product")
            st.write(f"The worst-performing product is: {data['worst_product']}")
            st.write("Review Summary:")
            st.write(data['worst_product_summary'])
            
            st.subheader("AI-Generated Insights and Recommendations")
            st.write(data['detailed_insights'])


def competitor_analysis():
    data = fetch_data("competitor_analysis", st.session_state.user_id)
    print("Data:", data)

    with st.expander("Competitor Analysis", expanded=True):
        col1, col2 = st.columns([3, 2])
        with col1:
            seller_sales = pd.Series(data['seller_sales'])
            fig = px.bar(seller_sales, x=seller_sales.index, y=seller_sales.values, title="Top 5 Sellers")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("AI Insight")
            st.write(data["brief_ai_insight"])
        
        if st.button("View Details for Competitor Analysis"):
            st.header("Competitor Analysis")
            
            seller_sales = pd.Series(data['seller_sales'])
            fig = px.bar(seller_sales, x=seller_sales.index, y=seller_sales.values, title="Top 5 Sellers")
            st.plotly_chart(fig)
            
            st.subheader("Top Seller's Best-Selling Products")
            st.write(data['top_seller_products'])
            
            st.subheader("AI-Generated Competitor Insights")
            st.write(data['detailed_insights'])


def customer_targeting():
    data = fetch_data("customer_targeting", st.session_state.user_id)
    print("Data:", data)

    with st.expander("Customer Targeting", expanded=True):
        col1, col2 = st.columns([3, 2])
        with col1:
            persona_counts = pd.Series(data['persona_counts'])
            fig = px.pie(values=persona_counts.values, names=persona_counts.index, title="Customer Personas")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("AI Insight")
            st.write(data["brief_ai_insight"])
        
        if st.button("View Details for Customer Targeting"):
            st.header("Customer Targeting")
            
            persona_counts = pd.Series(data['persona_counts'])
            fig = px.pie(values=persona_counts.values, names=persona_counts.index, title="Customer Personas")
            st.plotly_chart(fig)
            
            state_sales = pd.Series(data['state_sales'])
            fig = px.bar(state_sales, x=state_sales.index, y=state_sales.values, title="Top 5 States by Sales")
            st.plotly_chart(fig)
            
            st.subheader("AI-Generated Targeting Recommendations")
            st.write(data['detailed_insights'])


def supply_chain_optimization():
    data = fetch_data("supply_chain_optimization", st.session_state.user_id)
    print("Data:", data)
    
    with st.expander("Supply Chain Optimization", expanded=True):
        col1, col2 = st.columns([3, 2])
        with col1:
            customer_locations = pd.Series(data['customer_locations'])
            fig = px.bar(customer_locations, x=customer_locations.index, y=customer_locations.values, title="Top 10 Customer Zip Code Prefixes")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("AI Insight")
            st.write(data["brief_ai_insight"])
        
        if st.button("View Details for Supply Chain Optimization"):
            st.header("Supply Chain Optimization")
            
            customer_locations = pd.Series(data['customer_locations'])
            fig = px.bar(customer_locations, x=customer_locations.index, y=customer_locations.values, title="Top 10 Customer Zip Code Prefixes")
            st.plotly_chart(fig)
            
            seller_locations = pd.Series(data['seller_locations'])
            fig = px.bar(seller_locations, x=seller_locations.index, y=seller_locations.values, title="Top 10 Seller Zip Code Prefixes")
            st.plotly_chart(fig)
            
            st.subheader("AI-Generated Supply Chain Recommendations")
            st.write(data['detailed_insights'])


def seller_dashboard():
    st.title("Seller Dashboard")
    st.write("Welcome to your comprehensive seller analytics dashboard.")
    
    top_selling_products()
    worst_performing_products()
    competitor_analysis()
    customer_targeting()
    supply_chain_optimization()

seller_dashboard()
