import streamlit as st

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
