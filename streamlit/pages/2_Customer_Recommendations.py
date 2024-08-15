import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Set the API URL
API_URL = "http://localhost:8000"

# Fetch and resize images
def fetch_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

def resize_image(image, new_size):
    return image.resize(new_size)

# Check user authentication
if "user_type" not in st.session_state or st.session_state.user_type != "customer":
    st.switch_page("pages/1_Login.py")

if "user_id" not in st.session_state or not st.session_state.user_id:
    st.error("User ID not found. Please log in again.")
    st.switch_page("pages/1_Login.py")

# Create a logout button at the top right
col1, col2 = st.columns([8, 1])
with col2:
    if st.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()  # Refresh the page to apply changes

# Add a custom title with a different style
st.markdown("<h1 style='text-align: center; color: #007a99;'>Welcome to Your Personalized Shopping Experience!</h1>", unsafe_allow_html=True)

# Wrap the search bar and button in a single column with full width
search_query = st.text_input("Search for products", placeholder="Type here...", help="Search for your favorite items.")
search_button_col = st.columns([1])  # Single column to ensure full width
with search_button_col[0]:
    search_button_clicked = st.button("Search", use_container_width=True)

if search_button_clicked and search_query:
    # Store the search query in session state and redirect to search results page
    st.session_state.search_query = search_query
    st.switch_page("pages/4_Search_Results.py")

with st.spinner("Generating recommendations..."):
    # Fetch recommendations
    context_aware = requests.post(f"{API_URL}/context_aware_recommendations", json={"user_id": st.session_state.user_id}).json()
    order_history = requests.post(f"{API_URL}/content_filter_recommendations", json={"user_id": st.session_state.user_id}).json()
    collaborative = requests.post(f"{API_URL}/collaborative_filtering_recommendations", json={"user_id": st.session_state.user_id}).json()

# Add styled subheaders
st.markdown("### 🌟 Handpicked Recommendations for You!")
st.markdown("<hr style='border:1px solid #007a99;'>", unsafe_allow_html=True)

def display_product_strip(products, section_title):
    st.markdown(f"#### {section_title}")
    cols = st.columns(len(products))
    for col, product in zip(cols, products):
        with col:
            img = fetch_image(product['image_url'])
            resized_img = resize_image(img, (150, 150))
            st.image(resized_img, use_column_width=True)
            st.markdown(f"<p style='font-weight:bold; text-align:center;'>{product['name']}</p>", unsafe_allow_html=True)
            if st.button("View Details", key=product, help="Click to view more details."):
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
