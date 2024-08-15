import streamlit as st
import requests
from PIL import Image

API_URL = "http://localhost:8000"  # Update this with your FastAPI server URL

id_mapping = {
    "cst_demo": "548a09978548d2e347d494793e34c797",
    "seller_demo": "7d13fca15225358621be4086e1eb0964"
}

# Add your logo
logo = Image.open("/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/streamlit/pages/logo.jpeg")

# Create a sidebar
st.sidebar.image(logo, width=200)
st.sidebar.markdown("The Future of Shopping... has just Arrived. Welcome to SmartCommerce! ")
import base64
def set_bg_hack(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.
 
    Returns
    -------
    The background.
    '''
    # set bg name
    main_bg_ext = "png"
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

set_bg_hack('/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/streamlit/pages/background.jpg')
# # Custom CSS
st.markdown(
    """
    <style>
    .stButton > button {
        background-color: #008CBA;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #007a99;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Main content
st.markdown("<h1 style='text-align: center; color: #003563;'>Welcome to SmartCommerce!</h1>", unsafe_allow_html=True)

user_id = st.text_input("User ID", "")
password = st.text_input("Password", "", type="password")

if st.button("Login"):
    mapped_user_id = id_mapping.get(user_id, user_id)
    mapped_user_pass = id_mapping.get(password, password)
    response = requests.post(f"{API_URL}/authenticate", json={"user_id": mapped_user_id, "password": mapped_user_pass})
    if response.status_code == 200:
        st.session_state.user_type = response.json()["user_type"]
        st.session_state.user_id = mapped_user_id
        st.success("Login successful!")
        st.rerun()
    else:
        st.error("Invalid credentials. Please try again.")

if 'user_type' not in st.session_state:
    st.write("Please log in to continue.")
elif st.session_state.user_type == "customer":
        st.switch_page("pages/2_Customer_Recommendations.py")
elif st.session_state.user_type == "seller":
        st.switch_page("pages/5_Seller_Dashboard.py")
