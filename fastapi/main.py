from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from recommendation_systems.collaborative_filter import CollaborativeFilteringAgent
from recommendation_systems.content_filter import OrderHistoryAgent
from recommendation_systems.contextual_filter import ContextAwareAgent
from recommendation_systems.market_basket_analysis import MarketBasketAgent
import pandas as pd
import os
app = FastAPI()

# Get the current working directory
current_dir = os.getcwd()

# Construct the paths relative to the Final-Project-SmartCommerce directory

RAW_DATA_FOLDER_PATH = "/home/snehilaryan/final_pro/Final-Project-SmartCommerce/data_pipeline/data_files/raw/"
PROCESSED_DATA_FOLDER_PATH = "/home/snehilaryan/final_pro/Final-Project-SmartCommerce/data_pipeline/data_files/processed/"

# Load the preprocessed data
orders_full = pd.read_csv(PROCESSED_DATA_FOLDER_PATH + 'orders_full.csv')

class UserInput(BaseModel):
    user_id: str

@app.post("/authenticate")
async def authenticate_user(user_input: UserInput):
    if user_input.user_id in orders_full['customer_unique_id'].values:
        return {"user_type": "customer"}
    elif user_input.user_id in orders_full['seller_id'].values:
        return {"user_type": "seller"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/context_aware_recommendations")
async def get_context_aware_recommendations(user_input: UserInput):
    agent = ContextAwareAgent(orders_full)
    recommendations = agent.generate_city_insights_and_recommendations(user_input.user_id)
    return recommendations["popular_items"]

@app.post("/content_filter_recommendations")
async def get_order_history_recommendations(user_input: UserInput):
    agent = OrderHistoryAgent(orders_full)
    user_order_history = agent.get_user_order_history(user_input.user_id)
    similar_items = agent.get_similar_items(user_order_history)
    return similar_items

@app.post("/collaborative_filtering_recommendations")
async def get_collaborative_filtering_recommendations(user_input: UserInput):
    agent = CollaborativeFilteringAgent(orders_full)
    recommendations = agent.get_items_bought_by_similar_users(user_input.user_id)
    return recommendations

@app.post("/market_basket_recommendations")
async def get_market_basket_recommendations(user_input: UserInput):
    agent = MarketBasketAgent(orders_full)
    order_history_agent = OrderHistoryAgent(orders_full)
    user_order_history = order_history_agent.get_user_order_history(user_input.user_id)
    recommendations = agent.recommend(user_order_history)
    return recommendations

# 548a09978548d2e347d494793e34c797 - Customer
# 7d13fca15225358621be4086e1eb0964 - Seller