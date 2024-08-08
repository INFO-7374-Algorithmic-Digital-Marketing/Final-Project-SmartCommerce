import streamlit as st
import pandas as pd
from recsys_functions import (
    load_and_preprocess_data,
    ContextAwareAgent,
    OrderHistoryAgent,
    CollaborativeFilteringAgent,
    MarketBasketAgent,
    ExplanationAgent
)
# Streamlit app
st.title('Product Recommendation System')

# Input for User ID
user_id = st.text_input('Enter User ID:', '')

if user_id:
    with st.spinner('Generating recommendations...'):
        # Load data
        orders_full = load_and_preprocess_data()

        # Initialize agents
        agent = ContextAwareAgent(orders_full)
        context_aware_recommendations = agent.generate_city_insights_and_recommendations(user_id, date='2024-08-08')

        order_history_agent = OrderHistoryAgent(orders_full)
        user_order_history = order_history_agent.get_user_order_history(user_id)
        similar_items = order_history_agent.get_similar_items(user_order_history)

        collaborative_filtering_agent = CollaborativeFilteringAgent(orders_full)
        items_bought_by_similar_users = collaborative_filtering_agent.get_items_bought_by_similar_users(user_id)

        market_basket_agent = MarketBasketAgent(orders_full)
        market_basket_recommendations = market_basket_agent.recommend(user_order_history)

        explanation_agent = ExplanationAgent(
            context_aware_recommendations,
            similar_items,
            items_bought_by_similar_users,
            market_basket_recommendations,
            orders_full
        )
        recommendations = explanation_agent.generate_recommendations()
        explanation = explanation_agent.generate_explanation(recommendations)

        # Display explanation
        st.subheader('Product Recommendations')
        st.write(explanation)
