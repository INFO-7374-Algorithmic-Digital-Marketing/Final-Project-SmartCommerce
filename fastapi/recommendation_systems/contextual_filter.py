import logging
from datetime import datetime
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

    def generate_city_insights_and_recommendations(self, user_id):
        today_date = datetime.today().strftime('%Y-%m-%d')

        location = self.get_user_location(user_id)
        if not location:
            return "User location not found."

        # Fetch seasonal trends and recommendations
        seasonal_trends = self.fetch_seasonal_trends(location, today_date)
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
        # Get the top 10 product IDs based on popularity in the given location
        popular_item_ids = self.data[self.data['customer_city'] == location]['product_id'].value_counts().head(10).index.tolist()

        # Initialize an empty list to store detailed product information
        popular_items_details = []

        # Loop through each product ID and fetch the corresponding details
        for product_id in popular_item_ids:
            product_info = self.data[self.data['product_id'] == product_id].iloc[0]  # Assuming product_id is unique
            print(product_info.keys())
            product_details = {
                "product_id": product_info['product_id'],
                "name": product_info['title'],
                "description": product_info['shortDescription'],
                "image_url": product_info['imageUrl'],  # Replace with actual column name for image URL
                "link": product_info['itemWebUrl'],
                "avg_price": product_info["target_price"],            # Replace with actual column name for product link
                "summary": product_info['summary']
            }
            popular_items_details.append(product_details)

        logging.info(f"Popular items in location {location}: {popular_items_details}")
        return popular_items_details

# Columns Needed 
# customer_unique_id: Used to determine the user's location based on their unique ID.
# customer_city: Used to fetch the user's location and to find popular items in that location.
# product_id: Used to list the products related to specific trends, events, and social media mentions, as well as to find popular items by location.
# title: Used as the name of the product in the popular items by location.
# shortDescription: Used as the description of the product in the popular items by location.
# imageUrl: Used to provide the image URL of popular items by location.
# itemWebUrl: Used to provide the web link to the popular items by location.
# target_price: Used to include the average price of the popular items by location.
# summary: Included in the product details for the popular items by location.
