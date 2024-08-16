import streamlit as st

st.set_page_config(layout="wide", page_title="E-commerce Platform")

if "user_type" not in st.session_state:
    st.session_state.user_type = None

if st.session_state.user_type is None:
    st.switch_page("pages/1_Login.py")
else:
    st.title("E-commerce Platform")
    st.write(f"Welcome, {st.session_state.user_type}!")
    st.write("Please use the sidebar to navigate.")