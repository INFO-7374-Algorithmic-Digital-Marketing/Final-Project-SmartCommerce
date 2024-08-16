from fastapi import FastAPI, Request
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from recommendation_systems.collaborative_filter import CollaborativeFilteringAgent
from recommendation_systems.content_filter import OrderHistoryAgent
from recommendation_systems.contextual_filter import ContextAwareAgent
from recommendation_systems.market_basket_analysis import MarketBasketAgent
from search_engine.search_utils import get_search_results
import pandas as pd
import plotly.express as px
import numpy as np
import os
from abc import ABC, abstractmethod
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import plotly.express as px

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

RAW_DATA_FOLDER_PATH = os.getenv("RAW_DATA_FOLDER_PATH")
PROCESSED_DATA_FOLDER_PATH = os.getenv("PROCESSED_DATA_FOLDER_PATH")

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

class SearchRequest(BaseModel):
    query: str
    user_id: str

class LLMCaller(ABC):
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt

    @abstractmethod
    def call_llm(self, user_prompt):
        pass

class OpenAICaller(LLMCaller):
    def __init__(self, system_prompt):
        super().__init__(system_prompt)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def call_llm(self, user_prompt):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True
        )
        return ''.join(chunk.choices[0].delta.content or "" for chunk in response)

class GroqCaller(LLMCaller):
    def __init__(self, system_prompt):
        super().__init__(system_prompt)
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def call_llm(self, user_prompt):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        response = self.client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192"
        )
        return response.choices[0].message.content.strip()

def get_ai_insight(topic, data, insight_type="brief"):
    system_prompt = f"You are an AI assistant providing {'brief' if insight_type == 'brief' else 'detailed'} insights for an e-commerce seller dashboard."
    user_prompt = f"Based on the following data about {topic}, provide a {'brief ( 4-5 lines )' if insight_type == 'brief' else 'detailed and comprehensive ( 10 - 15lines)'} recommendation for the seller:\n\n{data}"
    
    llm_caller = OpenAICaller(system_prompt)  # or GroqCaller(system_prompt)
    return llm_caller.call_llm(user_prompt)

@app.post("/product_search")
async def product_search(request: SearchRequest):
    logging.info(f"Searching for products using embeddings for user_id: {request.user_id}")
    results = get_search_results(request.query, orders_full)
    if not results:
        raise HTTPException(status_code=404, detail="No products found")
    return results

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

@app.post("/top_selling_products")
async def top_selling_products(user_input: RecSysInput):
    df = orders_full[orders_full["seller_id"] == user_input.user_id]
    logging.info("Generating insights on top-selling products")
    product_sales = df.groupby('title')['target_price'].sum().sort_values(ascending=False).head(10)
    logging.info(f"Top-selling products: {product_sales}")
    top_product = product_sales.index[0]
    top_product_summary = df[df['title'] == top_product]['summary'].iloc[0]
    logging.info(f"Summary of top product: {top_product_summary}")

    # Generate AI insights
    brief_insight = get_ai_insight("Top Selling Products", product_sales.to_dict(), insight_type="brief")
    detailed_insight = get_ai_insight("Top Selling Products", product_sales.to_dict(), insight_type="detailed")

    result = {
        "product_sales": product_sales.to_dict(),
        "top_product": top_product,
        "top_product_summary": top_product_summary,
        "brief_ai_insight": brief_insight,
        "detailed_insights": detailed_insight
    }
    logging.info(f"Insights generated: {result}")
    return result

@app.post("/worst_performing_products")
async def worst_performing_products(user_input: RecSysInput):
    df = orders_full[orders_full["seller_id"] == user_input.user_id]
    logging.info("Generating insights on worst-performing products")
    product_sales = df.groupby('title')['target_price'].sum().sort_values().head(10)
    logging.info(f"Worst-performing products: {product_sales}")
    worst_product = product_sales.index[0]
    worst_product_summary = df[df['title'] == worst_product]['summary'].iloc[0]
    logging.info(f"Summary of worst product: {worst_product_summary}")

    # Generate AI insights
    brief_insight = get_ai_insight("Worst Performing Products", product_sales.to_dict(), insight_type="brief")
    detailed_insight = get_ai_insight("Worst Performing Products", product_sales.to_dict(), insight_type="detailed")

    result = {
        "product_sales": product_sales.to_dict(),
        "worst_product": worst_product,
        "worst_product_summary": worst_product_summary,
        "brief_ai_insight": brief_insight,
        "detailed_insights": detailed_insight
    }
    logging.info(f"Insights generated: {result}")
    return result

@app.post("/competitor_analysis")
async def competitor_analysis(user_input: RecSysInput):
    df = orders_full[orders_full["seller_id"] == user_input.user_id]
    logging.info("Generating insights on competitors")
    seller_sales = df.groupby('seller_id')['target_price'].sum().sort_values(ascending=False).head(5)
    logging.info(f"Top competitors: {seller_sales}")
    top_seller = seller_sales.index[0]
    top_seller_products = df[df['seller_id'] == top_seller]['title'].value_counts().head()

    # Generate AI insights
    brief_insight = get_ai_insight("Competitor Analysis", seller_sales.to_dict(), insight_type="brief")
    detailed_insight = get_ai_insight("Competitor Analysis", seller_sales.to_dict(), insight_type="detailed")

    result = {
        "seller_sales": seller_sales.to_dict(),
        "top_seller": top_seller,
        "top_seller_products": top_seller_products.to_dict(),
        "brief_ai_insight": brief_insight,
        "detailed_insights": detailed_insight
    }
    logging.info(f"Insights generated: {result}")
    return result

@app.post("/customer_targeting")
async def customer_targeting(user_input: RecSysInput):
    df = orders_full[orders_full["seller_id"] == user_input.user_id]
    logging.info("Generating insights on customer targeting")
    persona_counts = df['persona_column'].value_counts()
    state_sales = df.groupby('customer_state')['target_price'].sum().sort_values(ascending=False).head(5)

    # Generate AI insights
    brief_insight = get_ai_insight("Customer Targeting", persona_counts.to_dict(), insight_type="brief")
    detailed_insight = get_ai_insight("Customer Targeting", persona_counts.to_dict(), insight_type="detailed")

    result = {
        "persona_counts": persona_counts.to_dict(),
        "top_persona": persona_counts.index[0],
        "state_sales": state_sales.to_dict(),
        "brief_ai_insight": brief_insight,
        "detailed_insights": detailed_insight
    }
    logging.info(f"Insights generated: {result}")
    return result

@app.post("/supply_chain_optimization")
async def supply_chain_optimization(user_input: RecSysInput):
    df = orders_full[orders_full["seller_id"] == user_input.user_id]
    logging.info("Generating insights on supply chain optimization")
    customer_locations = df['customer_zip_code_prefix'].value_counts().head(10)
    seller_locations = df['seller_zip_code_prefix'].value_counts().head(10)

    # Convert numpy types to Python native types
    customer_locations_dict = {str(key): int(value) for key, value in customer_locations.items()}
    seller_locations_dict = {str(key): int(value) for key, value in seller_locations.items()}

    # Generate AI insights
    brief_insight = get_ai_insight("Supply Chain Optimization", customer_locations_dict, insight_type="brief")
    detailed_insight = get_ai_insight("Supply Chain Optimization", customer_locations_dict, insight_type="detailed")

    result = {
        "customer_locations": customer_locations_dict,
        "seller_locations": seller_locations_dict,
        "top_customer_zip": str(customer_locations.index[0]),
        "top_seller_zip": str(seller_locations.index[0]),
        "brief_ai_insight": brief_insight,
        "detailed_insights": detailed_insight
    }
    logging.info(f"Insights generated: {result}")
    return result


################################################################################################################
# Adding the set of udf related api endpoints here. Future work could be to merge them
################################################################################################################

@app.post("/product_search_udf")
async def product_search_udf(request: Request):
    data = await request.json()
    user_id = data['data'][0][1]
    query = data['data'][0][2]  
    results = get_search_results(query, orders_full)
    if not results:
        raise HTTPException(status_code=404, detail="No products found")
    return {"data": [[0, results]]}

from fastapi import Request

# Existing endpoints remain the same

@app.post("/product_search_udf")
async def product_search_udf(request: Request):
    data = await request.json()
    user_id = data['data'][0][1]
    query = data['data'][0][2]  
    results = get_search_results(query, orders_full)
    if not results:
        raise HTTPException(status_code=404, detail="No products found")
    return {"data": [[0, results]]}

@app.post("/authenticate_udf")
async def authenticate_user_udf(request: Request):
    data = await request.json()
    user_id = data['data'][0][1]
    password = data['data'][0][2]
    
    if user_id != password:
        return {"data": [[0, {"error": "Invalid credentials"}]]}

    if user_id in orders_full['customer_unique_id'].values:
        return {"data": [[0, {"user_type": "customer"}]]}
    elif user_id in orders_full['seller_id'].values:
        return {"data": [[0, {"user_type": "seller"}]]}
    else:
        return {"data": [[0, {"error": "User not found"}]]}

@app.post("/context_aware_recommendations_udf")
async def get_context_aware_recommendations_udf(request: Request):
    data = await request.json()
    user_id = data['data'][0][1]
    agent = ContextAwareAgent(orders_full)
    recommendations = agent.generate_city_insights_and_recommendations(user_id)
    return {"data": [[0, recommendations["popular_items"]]]}

@app.post("/content_filter_recommendations_udf")
async def get_order_history_recommendations_udf(request: Request):
    data = await request.json()
    user_id = data['data'][0][1]
    agent = OrderHistoryAgent(orders_full)
    user_order_history = agent.get_user_order_history(user_id)
    similar_items = agent.get_similar_items(user_order_history)
    return {"data": [[0, similar_items]]}

@app.post("/collaborative_filtering_recommendations_udf")
async def get_collaborative_filtering_recommendations_udf(request: Request):
    data = await request.json()
    user_id = data['data'][0][1]
    agent = CollaborativeFilteringAgent(orders_full)
    recommendations = agent.get_items_bought_by_similar_users(user_id)
    return {"data": [[0, recommendations]]}

@app.post("/market_basket_recommendations_udf")
async def get_market_basket_recommendations_udf(request: Request):
    data = await request.json()
    user_id = data['data'][0][1]
    agent = MarketBasketAgent(orders_full)
    order_history_agent = OrderHistoryAgent(orders_full)
    user_order_history = order_history_agent.get_user_order_history(user_id)
    recommendations = agent.recommend(user_order_history)
    return {"data": [[0, recommendations]]}

@app.post("/top_selling_products_udf")
async def top_selling_products_udf(request: Request):
    data = await request.json()
    user_id = data['data'][0][1]
    df = orders_full[orders_full["seller_id"] == user_id]
    product_sales = df.groupby('title')['target_price'].sum().sort_values(ascending=False).head(10)
    top_product = product_sales.index[0]
    top_product_summary = df[df['title'] == top_product]['summary'].iloc[0]

    brief_insight = get_ai_insight("Top Selling Products", product_sales.to_dict(), insight_type="brief")
    detailed_insight = get_ai_insight("Top Selling Products", product_sales.to_dict(), insight_type="detailed")

    result = {
        "product_sales": product_sales.to_dict(),
        "top_product": top_product,
        "top_product_summary": top_product_summary,
        "brief_ai_insight": brief_insight,
        "detailed_insights": detailed_insight
    }
    return {"data": [[0, result]]}

@app.post("/worst_performing_products_udf")
async def worst_performing_products_udf(request: Request):
    data = await request.json()
    user_id = data['data'][0][1]
    df = orders_full[orders_full["seller_id"] == user_id]
    product_sales = df.groupby('title')['target_price'].sum().sort_values().head(10)
    worst_product = product_sales.index[0]
    worst_product_summary = df[df['title'] == worst_product]['summary'].iloc[0]

    brief_insight = get_ai_insight("Worst Performing Products", product_sales.to_dict(), insight_type="brief")
    detailed_insight = get_ai_insight("Worst Performing Products", product_sales.to_dict(), insight_type="detailed")

    result = {
        "product_sales": product_sales.to_dict(),
        "worst_product": worst_product,
        "worst_product_summary": worst_product_summary,
        "brief_ai_insight": brief_insight,
        "detailed_insights": detailed_insight
    }
    return {"data": [[0, result]]}

@app.post("/competitor_analysis_udf")
async def competitor_analysis_udf(request: Request):
    data = await request.json()
    user_id = data['data'][0][1]
    df = orders_full[orders_full["seller_id"] == user_id]
    seller_sales = df.groupby('seller_id')['target_price'].sum().sort_values(ascending=False).head(5)
    top_seller = seller_sales.index[0]
    top_seller_products = df[df['seller_id'] == top_seller]['title'].value_counts().head()

    brief_insight = get_ai_insight("Competitor Analysis", seller_sales.to_dict(), insight_type="brief")
    detailed_insight = get_ai_insight("Competitor Analysis", seller_sales.to_dict(), insight_type="detailed")

    result = {
        "seller_sales": seller_sales.to_dict(),
        "top_seller": top_seller,
        "top_seller_products": top_seller_products.to_dict(),
        "brief_ai_insight": brief_insight,
        "detailed_insights": detailed_insight
    }
    return {"data": [[0, result]]}

@app.post("/customer_targeting_udf")
async def customer_targeting_udf(request: Request):
    data = await request.json()
    user_id = data['data'][0][1]
    df = orders_full[orders_full["seller_id"] == user_id]
    persona_counts = df['persona_column'].value_counts()
    state_sales = df.groupby('customer_state')['target_price'].sum().sort_values(ascending=False).head(5)

    brief_insight = get_ai_insight("Customer Targeting", persona_counts.to_dict(), insight_type="brief")
    detailed_insight = get_ai_insight("Customer Targeting", persona_counts.to_dict(), insight_type="detailed")

    result = {
        "persona_counts": persona_counts.to_dict(),
        "top_persona": persona_counts.index[0],
        "state_sales": state_sales.to_dict(),
        "brief_ai_insight": brief_insight,
        "detailed_insights": detailed_insight
    }
    return {"data": [[0, result]]}

@app.post("/supply_chain_optimization_udf")
async def supply_chain_optimization_udf(request: Request):
    data = await request.json()
    user_id = data['data'][0][1]
    df = orders_full[orders_full["seller_id"] == user_id]
    customer_locations = df['customer_zip_code_prefix'].value_counts().head(10)
    seller_locations = df['seller_zip_code_prefix'].value_counts().head(10)

    customer_locations_dict = {str(key): int(value) for key, value in customer_locations.items()}
    seller_locations_dict = {str(key): int(value) for key, value in seller_locations.items()}

    brief_insight = get_ai_insight("Supply Chain Optimization", customer_locations_dict, insight_type="brief")
    detailed_insight = get_ai_insight("Supply Chain Optimization", customer_locations_dict, insight_type="detailed")

    result = {
        "customer_locations": customer_locations_dict,
        "seller_locations": seller_locations_dict,
        "top_customer_zip": str(customer_locations.index[0]),
        "top_seller_zip": str(seller_locations.index[0]),
        "brief_ai_insight": brief_insight,
        "detailed_insights": detailed_insight
    }
    return {"data": [[0, result]]}