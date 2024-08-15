# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from recommendation_systems.collaborative_filter import CollaborativeFilteringAgent
# from recommendation_systems.content_filter import OrderHistoryAgent
# from recommendation_systems.contextual_filter import ContextAwareAgent
# from recommendation_systems.market_basket_analysis import MarketBasketAgent
# import pandas as pd

# app = FastAPI()

# RAW_DATA_FOLDER_PATH = '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/data_pipeline/data_files/raw/'
# PROCESSED_DATA_FOLDER_PATH = '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/data_pipeline/data_files/processed/'

# # Load the preprocessed data
# orders_full = pd.read_csv(PROCESSED_DATA_FOLDER_PATH + 'orders_full.csv')

# class UserInput(BaseModel):
#     user_id: str
#     password: str

# @app.post("/authenticate")
# async def authenticate_user(user_input: UserInput):
#     print(user_input.user_id, user_input.password)
#     if user_input.user_id != user_input.password:
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     if user_input.user_id in orders_full['customer_unique_id'].values:
#         return {"user_type": "customer"}
#     elif user_input.user_id in orders_full['seller_id'].values:
#         return {"user_type": "seller"}
#     else:
#         raise HTTPException(status_code=404, detail="User not found")


# @app.post("/context_aware_recommendations")
# async def get_context_aware_recommendations(user_input: UserInput):
#     agent = ContextAwareAgent(orders_full)
#     recommendations = agent.generate_city_insights_and_recommendations(user_input.user_id)
#     return recommendations["popular_items"]

# @app.post("/content_filter_recommendations")
# async def get_order_history_recommendations(user_input: UserInput):
#     agent = OrderHistoryAgent(orders_full)
#     user_order_history = agent.get_user_order_history(user_input.user_id)
#     similar_items = agent.get_similar_items(user_order_history)
#     return similar_items

# @app.post("/collaborative_filtering_recommendations")
# async def get_collaborative_filtering_recommendations(user_input: UserInput):
#     agent = CollaborativeFilteringAgent(orders_full)
#     recommendations = agent.get_items_bought_by_similar_users(user_input.user_id)
#     return recommendations

# @app.post("/market_basket_recommendations")
# async def get_market_basket_recommendations(user_input: UserInput):
#     agent = MarketBasketAgent(orders_full)
#     order_history_agent = OrderHistoryAgent(orders_full)
#     user_order_history = order_history_agent.get_user_order_history(user_input.user_id)
#     recommendations = agent.recommend(user_order_history)
#     return recommendations

# # 548a09978548d2e347d494793e34c797 - Customer
# # 7d13fca15225358621be4086e1eb0964 - Seller

import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from recommendation_systems.collaborative_filter import CollaborativeFilteringAgent
from recommendation_systems.content_filter import OrderHistoryAgent
from recommendation_systems.contextual_filter import ContextAwareAgent
from recommendation_systems.market_basket_analysis import MarketBasketAgent
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

RAW_DATA_FOLDER_PATH = '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/data_pipeline/data_files/raw/'
PROCESSED_DATA_FOLDER_PATH = '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/data_pipeline/data_files/processed/'

# Load the preprocessed data
logging.info("Loading preprocessed data from CSV files")
try:
    orders_full = pd.read_csv(PROCESSED_DATA_FOLDER_PATH + 'orders_full.csv')
    logging.info("Data loaded successfully")
except Exception as e:
    logging.error(f"Error loading data: {e}")
    raise

class UserInput(BaseModel):
    user_id: str
    password: str

class RecSysInput(BaseModel):
    user_id: str

@app.post("/authenticate")
async def authenticate_user(user_input: UserInput):
    logging.info(f"Authentication attempt for user_id: {user_input.user_id}")
    if user_input.user_id != user_input.password:
        logging.warning("Invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user_input.user_id in orders_full['customer_unique_id'].values:
        logging.info("User authenticated as customer")
        return {"user_type": "customer"}
    elif user_input.user_id in orders_full['seller_id'].values:
        logging.info("User authenticated as seller")
        return {"user_type": "seller"}
    else:
        logging.warning("User not found")
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/context_aware_recommendations")
async def get_context_aware_recommendations(user_input: RecSysInput):
    logging.info(f"Generating context-aware recommendations for user_id: {user_input.user_id}")
    agent = ContextAwareAgent(orders_full)
    recommendations = agent.generate_city_insights_and_recommendations(user_input.user_id)
    logging.info(f"Recommendations generated: {recommendations['popular_items']}")
    return recommendations["popular_items"]

@app.post("/content_filter_recommendations")
async def get_order_history_recommendations(user_input: RecSysInput):
    logging.info(f"Generating content-based recommendations for user_id: {user_input.user_id}")
    agent = OrderHistoryAgent(orders_full)
    user_order_history = agent.get_user_order_history(user_input.user_id)
    similar_items = agent.get_similar_items(user_order_history)
    logging.info(f"Recommendations generated: {similar_items}")
    return similar_items

@app.post("/collaborative_filtering_recommendations")
async def get_collaborative_filtering_recommendations(user_input: RecSysInput):
    logging.info(f"Generating collaborative filtering recommendations for user_id: {user_input.user_id}")
    agent = CollaborativeFilteringAgent(orders_full)
    recommendations = agent.get_items_bought_by_similar_users(user_input.user_id)
    logging.info(f"Recommendations generated: {recommendations}")
    return recommendations

@app.post("/market_basket_recommendations")
async def get_market_basket_recommendations(user_input: RecSysInput):
    logging.info(f"Generating market basket recommendations for user_id: {user_input.user_id}")
    agent = MarketBasketAgent(orders_full)
    order_history_agent = OrderHistoryAgent(orders_full)
    user_order_history = order_history_agent.get_user_order_history(user_input.user_id)
    recommendations = agent.recommend(user_order_history)
    logging.info(f"Recommendations generated: {recommendations}")
    return recommendations
