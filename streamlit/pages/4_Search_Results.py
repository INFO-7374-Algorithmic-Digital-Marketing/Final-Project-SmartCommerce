import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import datetime
import datetime
from streamlit import cache_data
import json


# Set the API URL
API_URL = "http://localhost:8000"

# Fetch and resize images
def fetch_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

def resize_image(image, new_size):
    return image.resize(new_size)

# Function to log actions
def log_action(action_type, product=None, search_query=None):
    today_date = datetime.datetime.now().date().isoformat()  # Get today's date
    log_entry = {
        "user_id": st.session_state.user_id,
        "action": action_type,
        "timestamp": datetime.datetime.now().isoformat(),
        "date": today_date  # Add today's date
    }
    if product:
        log_entry["product_name"] = product
    if search_query:
        log_entry["search_query"] = search_query
    st.session_state.user_log.append(log_entry)

# Add a Logs button to the sidebar
with st.sidebar:
    show_logs = st.checkbox("Show User Journey")

    if show_logs:
        st.write("### User Journey")
        if st.session_state.user_log:
            for log in st.session_state.user_log:
                st.write(f"**Date:** {log['date']}")
                st.write(f"**Action:** {log['action']}")
                st.write(f"**Timestamp:** {log['timestamp']}")
                if "product_name" in log:
                    st.write(f"**Product Name:** {log['product_name']}")
                if "search_query" in log:
                    st.write(f"**Search Query:** {log['search_query']}")
                st.write("---")
        else:
            st.write("No actions logged yet.")

# Check if we have a search query
if 'search_query' not in st.session_state:
    st.error("No search query found. Please go back to the main page and perform a search.")
    if st.button("Go back to main page"):
        st.switch_page("Main_Page.py")
else:
    search_query = st.session_state.search_query
    st.title(f"Search Results for '{search_query}'")

    # Perform the search
    with st.spinner("Searching for products..."):
        search_results = requests.post(f"{API_URL}/product_search", 
                                       json={"user_id": st.session_state.user_id, 
                                             "query": search_query}).json()

    if search_results:
        for product in search_results:
            col1, col2 = st.columns([1, 3])
            with col1:
                img = fetch_image(product['image_url'])
                resized_img = resize_image(img, (150, 150))
                st.image(resized_img)
            with col2:
                st.subheader(product['name'])
                st.write(f"**Category:** {product['category']}")
                st.write(f"**Price:** ${product['avg_price']:.2f}")
                st.write(f"**Description:** {product['description'][:100]}...")
                if st.button("View Details", key=product['product_id']):
                    log_action("view_details", product=product['name'])
                    st.session_state.selected_product = product
                    st.switch_page("pages/3_Product_Details.py")
        
        st.markdown("<hr>", unsafe_allow_html=True)
    else:
        st.warning("No results found for your search query.")

    if st.button("Back to Main Page"):
        st.session_state.selected_product = None  # Clear the selected product
        st.switch_page("pages/2_Customer_Recommendations.py")

# Add custom CSS styling
st.markdown(
    """
    <style>
    .stButton > button {
        background-color: #007a99;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        font-size: 14px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
        transition: all 0.3s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #005a73;
    }
    </style>
    """,
    unsafe_allow_html=True
)