import logging
from datetime import datetime
from tavily import TavilyClient, MissingAPIKeyError, InvalidAPIKeyError, UsageLimitExceededError
import logging
import pandas as pd
from abc import ABC, abstractmethod
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv
import pandas as pd
import os
import json 
import random 

load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
            stream=True,
            response_format={"type": "json_object"}
        )
        return ''.join(chunk.choices[0].delta.content or "" for chunk in response)

class ContextAwareAgent:
    def __init__(self, data):
        self.data = data
        try:
            self.tavily_client = TavilyClient(api_key="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")
        except MissingAPIKeyError:
            logging.error("API key is missing. Please provide a valid API key.")
        except InvalidAPIKeyError:
            logging.error("Invalid API key provided. Please check your API key.")
        except UsageLimitExceededError:
            logging.error("Usage limit exceeded. Please check your plan's usage limits or consider upgrading.")

    def call_gpt4o_for_top_categories(self, seasonal_output, event_output, social_media_output, persona_column):
        # Define system and user prompts
        system_prompt = "You are an expert in analyzing e-commerce data."
        user_prompt = f"""
        Here are the seasonal trends: {seasonal_output}
        Here are the event-based recommendations: {event_output}
        Here are the social media trends: {social_media_output}
        
        These are the available product categories: {self.data['product_category_name_english'].unique().tolist()}
        The user's persona is: {persona_column}
        
        Based on this information, can you identify the top 5 product categories that are most relevant to the user?
        Strictly return the output as json dict. 
        """
        print("user prompt", user_prompt)

        # Initialize the LLM caller
        llm_caller = OpenAICaller(system_prompt)

        # Call the LLM and get the response
        llm_response = llm_caller.call_llm(user_prompt)

        print("LLM response", llm_response)

        # Parse the JSON response
        try:
            response_json = json.loads(llm_response)
            top_5_categories = response_json.get('top_product_categories', self.data['product_category_name_english'].unique().tolist())
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from LLM response.")
            top_5_categories = self.data['product_category_name_english'].unique().tolist()
            return None

        # Filter the top products from the city that fall into those categories
        filtered_products = self.data[self.data['product_category_name_english'].isin(top_5_categories)]

        return {
            "top_5_categories": top_5_categories,
            "filtered_products": filtered_products
        }

    def get_user_location(self, user_id):
        try:
            user_location = self.data[self.data['customer_unique_id'] == user_id]['customer_city'].iloc[0]
            logging.info(f"User location for user_id {user_id}: {user_location}")
            return user_location
        except IndexError:
            logging.error(f"User ID {user_id} not found in the data.")
            return None

    def fetch_seasonal_trends(self, location, date):
        try:
            query = f"Seasonal trends in {location} on {date}"
            response = self.tavily_client.qna_search(query=query)
            logging.info(f"Seasonal trends for {location} on {date}: {response}")
            return response
        except Exception as e:
            logging.error(f"Failed to fetch seasonal trends: {e}")
            return "General Essentials"

    def fetch_event_based_recommendations(self, location):
        try:
            query = f"Events happening in {location} this week"
            response = self.tavily_client.qna_search(query=query)
            logging.info(f"Event-based recommendations for {location}: {response}")
            return response
        except Exception as e:
            logging.error(f"Failed to fetch event-based recommendations: {e}")
            return "General Events"

    def fetch_social_media_trends(self, location):
        try:
            query = f"Social media trends in {location}"
            response = self.tavily_client.qna_search(query=query)
            logging.info(f"Social media trends for {location}: {response}")
            return response
        except Exception as e:
            logging.error(f"Failed to fetch social media trends: {e}")
            return "General Trends"

    def generate_city_insights_and_recommendations(self, user_id):
        today_date = datetime.today().strftime('%Y-%m-%d')

        location = self.get_user_location(user_id)
        if not location:
            return "User location not found."

        # Get popular items based on these categories
        popular_items = self.get_popular_items_by_location(location)

        return popular_items

    def get_popular_items_by_location(self, location, num_of_items=6):
        self.data['summary'] = self.data['summary'].fillna("No review summary available")
        # Get seasonal, event-based, and social media trends
        if os.getenv("USE_TAVILY"):
            seasonal_output = self.fetch_seasonal_trends(location, datetime.today().strftime('%Y-%m-%d'))
            event_output = self.fetch_event_based_recommendations(location)
            social_media_output = self.fetch_social_media_trends(location)

            # Call GPT-4o to get the top 5 recommended categories
            result = self.call_gpt4o_for_top_categories(seasonal_output, event_output, social_media_output, "persona_column")
        else:
            all_categories = self.data['product_category_name_english'].unique().tolist()
            result = {
                "top_5_categories": random.sample(all_categories, min(7, len(all_categories)))[:5]
            }
        if not result:
            logging.error("Failed to get recommended categories from GPT-4o.")
            return []

        recommended_categories = result["top_5_categories"]

        # Filter products by location and recommended categories
        filtered_data = self.data[(self.data['customer_city'] == location) &
                                (self.data['product_category_name_english'].isin(recommended_categories))]

        # Get the top product IDs based on popularity in the given location
        popular_item_ids = filtered_data['product_id'].value_counts().head(num_of_items).index.tolist()

        # Initialize an empty list to store detailed product information
        popular_items_details = []

        for product_id in popular_item_ids:
            product_info = self.data[self.data['product_id'] == product_id].iloc[0]  # Assuming product_id is unique
            product_details = {
                "product_id": product_info['product_id'],
                "name": product_info['title'],
                "description": product_info['shortDescription'],
                "image_url": product_info['imageUrl'],  # Replace with actual column name for image URL
                "link": product_info['itemWebUrl'],
                "avg_price": product_info["target_price"],  # Replace with actual column name for product link
                "summary": product_info['summary']
            }
            popular_items_details.append(product_details)

        logging.info(f"Popular items in location {location} based on recommended categories: {popular_items_details}")
        return popular_items_details
