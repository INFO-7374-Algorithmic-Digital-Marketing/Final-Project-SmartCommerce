import streamlit as st

if "selected_product" not in st.session_state:
    st.error("No product selected. Please go back and select a product.")
    st.stop()

product = st.session_state.selected_product

st.title(f"Product Details for {product['name']}")

st.image(product['image_url'], use_column_width=True)
st.write(f"**Name:** {product['name']}")
st.write(f"**Description:** {product['description']}")
st.write(f"**Price:** ${product['avg_price']:.2f}")
st.write(f"**Link:** [View on Store]({product['link']})")
st.write("Go back to the previous page to see more recommendations.")
st.write(f"**Customers Say:** {product['summary']}")

# Adding a "Back" button
if st.button("Back"):
    st.session_state.selected_product = None  # Clear the selected product
    st.switch_page("pages/2_Customer_Recommendations.py")
