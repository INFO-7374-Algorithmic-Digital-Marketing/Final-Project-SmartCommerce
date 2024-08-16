import streamlit as st

if "user_type" not in st.session_state or st.session_state.user_type != "customer":
    st.switch_page("pages/1_Login.py")

st.title("Customer Service Chatbot")

user_query = st.text_input("Ask your question here")
if user_query:
    st.write("Chatbot: Thank you for your question. Our support team will get back to you shortly.")