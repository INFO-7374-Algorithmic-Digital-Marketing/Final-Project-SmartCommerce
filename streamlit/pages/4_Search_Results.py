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
                    st.session_state.selected_product = product
                    st.switch_page("pages/3_Product_Details.py")
        
        st.markdown("<hr>", unsafe_allow_html=True)
    else:
        st.warning("No results found for your search query.")

    if st.button("Back to Main Page"):
        del st.session_state['search_query']
        st.switch_page("Main_Page.py")

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