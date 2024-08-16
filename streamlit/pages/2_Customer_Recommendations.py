import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import datetime
from streamlit import cache_data
import json

# Set the API URL
API_URL = "http://localhost:8000"
USER_LOGS = "/home/ubuntu/Final-Project-SmartCommerce/logging/"

if "show_logs" not in st.session_state:
    st.session_state.show_logs = False  # Toggle to show/hide logs

@cache_data(ttl=3600)  # Cache for 1 hour
def get_context_aware_recommendations(user_id):
    return requests.post(f"{API_URL}/context_aware_recommendations", json={"user_id": user_id}).json()

@cache_data(ttl=3600)  # Cache for 1 hour
def get_content_filter_recommendations(user_id):
    return requests.post(f"{API_URL}/content_filter_recommendations", json={"user_id": user_id}).json()

@cache_data(ttl=3600)  # Cache for 1 hour
def get_collaborative_filtering_recommendations(user_id):
    return requests.post(f"{API_URL}/collaborative_filtering_recommendations", json={"user_id": user_id}).json()
    

# Fetch and resize images
def fetch_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

def resize_image(image, new_size):
    return image.resize(new_size)

def save_logs():
    # Save the log somewhere, e.g., a file or database
    print("Saving User Session Logs")
    today_date = datetime.datetime.now().date().isoformat()  # Get today's date
    file_name = f"user_logs_{st.session_state.user_id}_{today_date}.json"
    with open(file_name, "w") as f:
        json.dump(st.session_state.user_log, f)

# Check user authentication
if "user_type" not in st.session_state or st.session_state.user_type != "customer":
    st.switch_page("pages/1_Login.py")

if "user_id" not in st.session_state or not st.session_state.user_id:
    st.error("User ID not found. Please log in again.")
    st.switch_page("pages/1_Login.py")

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

# Create a logout button at the top right
col1, col2 = st.columns([8, 1])
with col2:
    logout_clicked = st.button("Logout")
    if logout_clicked:
        save_logs()
        st.session_state.clear()  # Clear all session state variables
        st.rerun()  # Refresh the page to apply changes

# Add a custom title with a different style
st.markdown("<h1 style='text-align: center; color: #007a99;'>Welcome to Your Personalized Shopping Experience!</h1>", unsafe_allow_html=True)

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

# Wrap the search bar and button in a single column with full width
search_query = st.text_input("Search for products", placeholder="Type here...", help="Search for your favorite items.")
search_button_col = st.columns([1])  # Single column to ensure full width
with search_button_col[0]:
    search_button_clicked = st.button("Search", use_container_width=True)

if search_button_clicked and search_query:
    # Store the search query in session state and redirect to search results page
    log_action("search", search_query)
    st.session_state.search_query = search_query
    st.switch_page("pages/4_Search_Results.py")

with st.spinner("Generating recommendations..."):
    # Fetch recommendations using cached functions
    context_aware = get_context_aware_recommendations(st.session_state.user_id)
    order_history = get_content_filter_recommendations(st.session_state.user_id)
    collaborative = get_collaborative_filtering_recommendations(st.session_state.user_id)# Add styled subheaders

st.markdown("### 🌟 Handpicked Recommendations for You!")
st.markdown("<hr style='border:1px solid #007a99;'>", unsafe_allow_html=True)

def truncate_product_name(name, max_length=45):
    if len(name) > max_length:
        return name[:max_length] + "..."
    else:
        return name

def display_product_strip(products, section_title):
    st.markdown(f"#### {section_title}")
    cols = st.columns(len(products))
    for col, product in zip(cols, products):
        with col:
            img = fetch_image(product['image_url'])
            resized_img = resize_image(img, (150, 150))
            st.image(resized_img, use_column_width=True)
            st.markdown(f"<p style='font-weight:bold; text-align:center;'>{truncate_product_name(product['name'])}</p>", unsafe_allow_html=True)
            if st.button("View Details", key=product, help="Click to view more details."):
                log_action("view_details", product=product['name'])
                st.session_state.selected_product = product
                st.switch_page("pages/3_Product_Details.py")
    st.markdown("<hr>", unsafe_allow_html=True)

# Display product strips with different categories
display_product_strip(context_aware, "Most Popular Items in Your City")
display_product_strip(collaborative, "Items Loved by Users like You")
display_product_strip(order_history, "New Arrivals Inspired by Your Recent Purchases")

# Add custom CSS styling
st.markdown(
    """
    <style>
    /* Align text to center */
    .stRadio label, .stTextInput label, .stButton button, .stMarkdown p {
        text-align: center;
    }
    /* Add padding and shadow to images */
    .stImage {
        border-radius: 10px;
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
    }
    /* Style the buttons */
    div.stButton > button {
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
    div.stButton > button:hover {
        background-color: #007a99;
    }
    /* Add hover effect to the text */
    .stMarkdown p:hover {
        color: #007a99;
    }
    </style>
    """,
    unsafe_allow_html=True
)
