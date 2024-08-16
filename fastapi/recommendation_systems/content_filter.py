import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Order History Agent
class OrderHistoryAgent:
    def __init__(self, data):
        self.data = data

    def get_user_order_history(self, user_id):
        order_history = self.data[self.data['customer_unique_id'] == user_id]['product_id'].tolist()
        logging.info(f"Order history for user_id {user_id}: {order_history}")
        return order_history

    def get_similar_items(self, order_history, num_of_items=6):
        print(self.data.columns)    
        # Step 1: Get the list of unique categories from the user's order history
        user_categories = self.data[self.data['product_id'].isin(order_history)]['product_category_name_english'].unique().tolist()

        # Step 2: Filter products that belong to these categories
        similar_items = self.data[self.data['product_category_name_english'].isin(user_categories)]

        # Step 3: Group by product_id and calculate the average sentiment score
        similar_items = similar_items.groupby('product_id')['avg_sentiment_score'].mean().reset_index()

        # Step 4: Sort by sentiment score and select the top 10 products
        top_similar_items = similar_items.sort_values(by='avg_sentiment_score', ascending=False).head(num_of_items)['product_id'].tolist()

        # Step 5: Get detailed information for each of the top similar products
        similar_items_details = []
        for product_id in top_similar_items:
            product_info = self.data[self.data['product_id'] == product_id].iloc[0]
            product_details = {
                "product_id": product_info['product_id'],
                "name": product_info['title'],
                "description": product_info['shortDescription'],
                "image_url": product_info['imageUrl'],  # Replace with actual column name for image URL
                "link": product_info['itemWebUrl'],           # Replace with actual column name for product link
                "avg_price": product_info['target_price'],
                "summary": product_info['summary']
            }
            similar_items_details.append(product_details)

        logging.info(f"Top similar items based on categories in order history: {similar_items_details}")
        return similar_items_details

# Columns Needed
# customer_unique_id: Used to filter the order history for a specific user.
# product_id: Used to list the products in the user's order history, filter similar items, and identify products for detailed information.
# product_category_name_english: Used to find the categories of products in the user's order history and filter similar items.
# avg_sentiment_score: Used to calculate the average sentiment score for similar items and to sort and select the top products.
# title: Used as the name of the product in the detailed information for similar items.
# shortDescription: Used as the description of the product in the detailed information for similar items.
# imageUrl: Used to provide the image URL of the similar items.
# itemWebUrl: Used to provide the web link to the similar items.
# target_price: Used to include the average price of the similar items in the detailed information.
# summary: Included in the product details for the similar items.
