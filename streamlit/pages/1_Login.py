import streamlit as st
import requests

API_URL = "http://localhost:8000"  # Update this with your FastAPI server URL

id_mapping = {
    "cst_demo": "548a09978548d2e347d494793e34c797",
    "seller_demo": "7d13fca15225358621be4086e1eb0964"
}


st.title("Login")

user_id = st.text_input("User ID")
password = st.text_input("Password", type="password")

if st.button("Login"):
    mapped_user_id = id_mapping.get(user_id, user_id)
    mapped_user_pass = id_mapping.get(password, password)
    response = requests.post(f"{API_URL}/authenticate", json={"user_id": mapped_user_id, "password": mapped_user_pass})
    if response.status_code == 200:
        print("Response:", response.json())
        print(response.json()["user_type"])
        st.session_state.user_type = response.json()["user_type"]
        st.session_state.user_id = mapped_user_id
        st.success("Login successful!")
        st.rerun()
    else:
        st.error("Invalid credentials. Please try again.")

if st.session_state == []:
    st.write("Please log in to continue.")
elif st.session_state.user_type == "customer":
        st.switch_page("pages/2_Customer_Recommendations.py")
elif st.session_state.user_type == "seller":
        st.switch_page("pages/4_Seller_Dashboard.py")
