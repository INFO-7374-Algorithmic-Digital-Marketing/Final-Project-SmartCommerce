import logging
import pandas as pd
import database

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CollaborativeFilteringAgent:
    def __init__(self, data):
        self.data = data
        self.user_personas = self._create_user_persona_dict()

    def _create_user_persona_dict(self):
        return self.data.groupby('customer_unique_id')['persona_column'].first().to_dict()

    def get_items_bought_by_similar_users(self, user_id, num_of_items=6):
        # import some churn detect fn 
        # get user id's churn flag
        user_personas = self.user_personas.get(user_id, 'General Consumer').split(', ')
        
        similar_users = [
            uid for uid, personas in self.user_personas.items()
            if uid != user_id and any(persona in personas for persona in user_personas)
        ]
        
        items_bought_by_similar_users = self.data[self.data['customer_unique_id'].isin(similar_users)]
        print("\n\n\nself.data.columns", self.data.columns)
        items_bought_by_similar_users = items_bought_by_similar_users.groupby('product_id').agg({
            'avg_sentiment_score': 'mean',
            'product_category_name_english': 'first',
            'target_price': 'mean',
            'title': 'first',
            'shortDescription': 'first',
            'imageUrl': 'first',
            'itemWebUrl': 'first',
            'summary': 'first'  # Include 'summary' in the aggregation
        }).reset_index()
        
        top_items = items_bought_by_similar_users.sort_values(by='avg_sentiment_score', ascending=False).head(num_of_items)
        
        recommended_items = []
        for _, item in top_items.iterrows():
            product_details = {
                "product_id": item['product_id'],
                "name": item['title'],
                "description": item['shortDescription'],
                "image_url": item['imageUrl'],
                "link": item['itemWebUrl'],
                "category": item['product_category_name_english'],
                "avg_sentiment_score": item['avg_sentiment_score'],
                "avg_price": item['target_price'],
                "summary": item['summary']
            }
            recommended_items.append(product_details)
        
        logging.info(f"Recommended items for user_id {user_id} (Personas: {user_personas}):")
        for item in recommended_items:
            logging.info(f"Product ID: {item['product_id']}, Name: {item['name']}, "
                         f"Category: {item['category']}, Avg. Sentiment: {item['avg_sentiment_score']:.2f}, "
                         f"Avg. Price: ${item['avg_price']:.2f}")
        
        return 
    


# Usage
# cf_agent = CollaborativeFilteringAgent(orders_full_with_personas)
# recommendations = cf_agent.get_items_bought_by_similar_users('some_user_id')

# Columns needed 
# customer_unique_id: Used to create a dictionary of user personas and to filter similar users.
# persona_column: Used to store personas for each customer.
# product_id: Used to group items bought by similar users and for the final product recommendations.
# avg_sentiment_score: Used to calculate the average sentiment score for each product and sort the recommendations.
# product_category_name_english: Used to include the product category in the recommendations.
# target_price: Used to calculate the average price of the recommended products.
# title: Used as the name of the product in the recommendations.
# shortDescription: Used as the description of the product in the recommendations.
# imageUrl: Used to provide the image URL of the recommended products.
# itemWebUrl: Used to provide the web link to the recommended products.
# summary: Included in the product details for the recommendations, though not shown in the logging output.
