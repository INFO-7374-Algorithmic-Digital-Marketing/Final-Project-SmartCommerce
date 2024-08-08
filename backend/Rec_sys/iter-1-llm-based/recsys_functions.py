from data_utils import load_and_preprocess_data, apriori_recommendation_system
import logging
from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import requests
import logging

import pandas as pd
import os
from openai import OpenAI
from abc import ABC, abstractmethod
import json

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
        # Join the response chunks and parse as JSON
        response_text = ''.join(chunk.choices[0].delta.content or "" for chunk in response)
        print(response_text)
        return response_text


class ContextAwareAgent:
    def __init__(self, data):
        self.data = data

    def get_user_location(self, user_id):
        try:
            user_location = self.data[self.data['customer_unique_id'] == user_id]['customer_city'].iloc[0]
            logging.info(f"User location for user_id {user_id}: {user_location}")
            return user_location
        except IndexError:
            logging.error(f"User ID {user_id} not found in the data.")
            return None

    def fetch_seasonal_trends(self, location, date):
        # Pseudocode for fetching seasonal trends based on location and date
        # This would typically involve an API call to a service that provides seasonal trend data
        # response = requests.get(f"https://api.tavily.com/seasons?location={location}&date={date}")
        # if response.status_code == 200:
        #     seasonal_trends = response.json()
        #     logging.info(f"Seasonal trends for {location} on {date}: {seasonal_trends}")
        #     return seasonal_trends
        # else:
        #     logging.error(f"Failed to fetch seasonal trends for {location}. Status code: {response.status_code}")
        #     return {}
        response = "Seasonal trends are :"
        return response
        

    def get_seasonal_product_recommendations(self, seasonal_trends):
        # Based on the seasonal trends, suggest relevant product categories
        if 'summer' in seasonal_trends:
            recommended_category = 'Cooling Appliances'
        elif 'winter' in seasonal_trends:
            recommended_category = 'Warm Clothing'
        else:
            recommended_category = 'General Essentials'
        logging.info(f"Recommended category based on seasonal trends: {recommended_category}")
        return recommended_category

    def fetch_event_based_recommendations(self, location):
        # Pseudocode for fetching events from Tavily or another API
        # response = requests.get(f"https://api.tavily.com/cities/{location}/events")
        # if response.status_code == 200:
        #     events = response.json()
        #     event_related_items = []
        #     for event in events:
        #         items = self.data[self.data['event'] == event]['product_id'].value_counts().head(10).index.tolist()
        #         event_related_items.extend(items)
        #     logging.info(f"Event-based items in {location}: {event_related_items}")
        #     return event_related_items
        # else:
        #     logging.error(f"Failed to fetch event data for {location}. Status code: {response.status_code}")
        #     return []
        response = "Event based recs are :"
        return response


    def fetch_social_media_trends(self, location):
        # Pseudocode for fetching social media trends
        # response = requests.get(f"https://api.socialmedia.com/trends?location={location}")
        # if response.status_code == 200:
        #     trending_topics = response.json().get('trending_topics', [])
        #     trending_items = self.data[self.data['tags'].isin(trending_topics)]['product_id'].value_counts().head(10).index.tolist()
        #     logging.info(f"Trending items in {location} based on social media: {trending_items}")
        #     return trending_items
        # else:
        #     logging.error(f"Failed to fetch social media trends for {location}. Status code: {response.status_code}")
        #     return []
        response = "Social media trends are :"
        return response

    def generate_city_insights_and_recommendations(self, user_id, date):

        location = self.get_user_location(user_id)
        if not location:
            return "User location not found."

        # Fetch seasonal trends and recommendations
        seasonal_trends = self.fetch_seasonal_trends(location, date)
        seasonal_recommendation = self.get_seasonal_product_recommendations(seasonal_trends)

        # Fetch event-based recommendations
        event_recommendations = self.fetch_event_based_recommendations(location)

        # Fetch social media trends and recommendations
        social_media_recommendations = self.fetch_social_media_trends(location)

        # Compile the insights and recommendations
        insights = {
            "location": location,
            "seasonal_recommendation": seasonal_recommendation,
            "event_recommendations": event_recommendations,
            "social_media_recommendations": social_media_recommendations,
            "popular_items": self.get_popular_items_by_location(location)
        }

        logging.info(f"Generated insights and recommendations for user_id {user_id}: {insights}")
        return insights

    def get_popular_items_by_location(self, location):
        popular_items = self.data[self.data['customer_city'] == location]['product_id'].value_counts().head(10).index.tolist()
        logging.info(f"Popular items in location {location}: {popular_items}")
        return popular_items

# Collaborative Filtering Agent
class CollaborativeFilteringAgent:
    def __init__(self, data):
        self.data = data

    def get_items_bought_by_similar_users(self, user_id):
        user_order_history = self.data[self.data['customer_unique_id'] == user_id]['product_id'].tolist()
        similar_users = self.data[self.data['product_id'].isin(user_order_history)]['customer_unique_id'].unique()
        items_bought_by_similar_users = self.data[self.data['customer_unique_id'].isin(similar_users)]
        items_bought_by_similar_users = items_bought_by_similar_users.groupby('product_id')['avg_sentiment_score'].mean().reset_index()
        items_bought_by_similar_users = items_bought_by_similar_users.sort_values(by='avg_sentiment_score', ascending=False).head(10)['product_id'].tolist()
        logging.info(f"Items bought by similar users for user_id {user_id}: {items_bought_by_similar_users}")
        return items_bought_by_similar_users

# Order History Agent
class OrderHistoryAgent:
    def __init__(self, data):
        self.data = data

    def get_user_order_history(self, user_id):
        order_history = self.data[self.data['customer_unique_id'] == user_id]['product_id'].tolist()
        logging.info(f"Order history for user_id {user_id}: {order_history}")
        return order_history

    def get_similar_items(self, order_history):
        similar_items = self.data[self.data['product_id'].isin(order_history)]
        similar_items = similar_items.groupby('product_id')['avg_sentiment_score'].mean().reset_index()
        similar_items = similar_items.sort_values(by='avg_sentiment_score', ascending=False).head(10)['product_id'].tolist()
        logging.info(f"Similar items based on order history: {similar_items}")
        return similar_items

class MarketBasketAgent:
    def __init__(self, data, min_support=0.0001):
        self.data = data
        self.min_support = min_support
        self.rules = self.generate_rules()

    def generate_rules(self):
        logging.info("Loading and preprocessing data for Apriori algorithm...")
        data = self.data.copy()
        data = data.head(30000)
        data['quantity'] = 1

        item_freq = data['product_id'].value_counts()
        data = data[data['product_id'].isin(item_freq.index[item_freq >= 10])]

        basket = (data.groupby(['order_id', 'product_id'])['quantity']
                  .sum().unstack().reset_index().fillna(0).set_index('order_id'))
        basket_sets = basket.map(lambda x: 1 if x >= 1 else 0).astype(bool)

        logging.info("Generating frequent itemsets...")
        frequent_itemsets = apriori(basket_sets, min_support=self.min_support, use_colnames=True)
        frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))

        logging.info("Generating association rules...")
        rules = association_rules(frequent_itemsets, metric='confidence', min_threshold=0.01)
        high_confidence_rules = rules[rules['confidence'] >= 0.05]
        logging.info(f"High confidence rules: {high_confidence_rules}")

        return high_confidence_rules

    def recommend(self, user_order_history):
        recommendations = set()
        logging.info(f"User order history: {user_order_history}")
        for item in user_order_history:
            matching_rules = self.rules[self.rules['antecedents'].apply(lambda x: item in x)]
            for _, rule in matching_rules.iterrows():
                recommendations.update(rule['consequents'])
        logging.info(f"Apriori recommendations: {recommendations}")
        return [item for item in recommendations if item not in user_order_history]


import logging
import json
from openai import OpenAI

class ExplanationAgent:
    def __init__(self, location_items, history_items, collaborative_items, market_basket_items, data):
        self.location_items = location_items
        self.history_items = history_items
        self.collaborative_items = collaborative_items
        self.market_basket_items = market_basket_items
        self.data = data
        self.llm_caller = OpenAICaller(system_prompt="Generate a user-friendly recommendation page based on the provided product details.")

    def generate_recommendations(self):
        recommendations = {
            "location_based": self.location_items,
            "history_based": self.history_items,
            "collaborative_based": self.collaborative_items,
            "market_basket_based": self.market_basket_items
        }
        logging.info(f"Generated recommendations: {recommendations}")
        return recommendations

    def generate_explanation(self, recommendations):
        # Get product information
        location_info = self.get_product_info(recommendations['location_based']['popular_items'])
        user_location = recommendations['location_based']['location']
        history_info = self.get_product_info(recommendations['history_based'])
        collaborative_info = self.get_product_info(recommendations['collaborative_based'])
        market_basket_info = self.get_product_info(recommendations['market_basket_based'])
        
        # Generate a detailed explanation
        prompt = self.create_prompt(location_info, history_info, collaborative_info, market_basket_info, user_location)
        explanation = self.call_gpt(prompt)
        logging.info(f"Generated explanation: {explanation}")
        return explanation

    def get_product_info(self, product_ids):
        product_info = self.data[self.data['product_id'].isin(product_ids)][['product_name', 'product_description']]
        return product_info.to_dict(orient='records')

    def create_prompt(self, location_info, history_info, collaborative_info, market_basket_info, user_location):
        prompt = (
            "I have run various algorithms to get recommendations for this user:\n\n"
            f"1. **Based off their Location {user_location}, the most popular items are:**\n"
            f"{self.format_product_info(location_info)}\n\n"
            "2. **Based off their order History-Based Recommendations:**\n"
            f"{self.format_product_info(history_info)}\n\n"
            "3. **Based on similar users order history : Collaborative-Based Recommendations:**\n"
            f"{self.format_product_info(collaborative_info)}\n\n"
            "4. **Based on Market Basket-Based Recommendations:**\n"
            f"{self.format_product_info(market_basket_info)}\n\n"
            "Please present this information in a user-friendly format in about 200 words, as if talking to the user, that hey we noticed that you are in location, the top products their would be xyz and so on."
        )
        return prompt

    def format_product_info(self, product_info):
        formatted_info = ""
        for item in product_info:
            formatted_info += (
                f"- **{item['product_name']}**: {item['product_description']}\n"
            )
        return formatted_info

    def call_gpt(self, prompt):
        return self.llm_caller.call_llm(prompt)



# # User ID for demonstration
# user_id = '451e48381edab7f1f6dbfa6d728616ff'  # Replace with an actual user ID from the dataset
# orders_full  = load_and_preprocess_data()

# # Assuming 'data' is a DataFrame containing customer and product information
# agent = ContextAwareAgent(orders_full)
# context_aware_recommendations = agent.generate_city_insights_and_recommendations(user_id, date='2024-08-08')

# # Instantiate and run the order history agent
# order_history_agent = OrderHistoryAgent(orders_full)
# user_order_history = order_history_agent.get_user_order_history(user_id)
# similar_items = order_history_agent.get_similar_items(user_order_history)

# # Instantiate and run the collaborative filtering agent
# collaborative_filtering_agent = CollaborativeFilteringAgent(orders_full)
# items_bought_by_similar_users = collaborative_filtering_agent.get_items_bought_by_similar_users(user_id)

# # Instantiate and run the market basket analysis agent
# market_basket_agent = MarketBasketAgent(orders_full)
# market_basket_recommendations = market_basket_agent.recommend(user_order_history)

# # Instantiate and run the explanation agent
# explanation_agent = ExplanationAgent(context_aware_recommendations, similar_items, items_bought_by_similar_users, market_basket_recommendations, orders_full)
# recommendations = explanation_agent.generate_recommendations()
# explanation = explanation_agent.generate_explanation(recommendations)

# print(explanation)