import pandas as pd
from textblob import TextBlob
from sklearn.preprocessing import StandardScaler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Data Ingestion and Preprocessing Function
def load_and_preprocess_data(file_paths):
    logging.info("Loading datasets...")
    
    # Load datasets
    customers = pd.read_csv(file_paths['customers'])
    order_items = pd.read_csv(file_paths['order_items'])
    order_payments = pd.read_csv(file_paths['order_payments'])
    order_reviews = pd.read_csv(file_paths['order_reviews'])
    orders = pd.read_csv(file_paths['orders'])
    products = pd.read_csv(file_paths['products'])
    sellers = pd.read_csv(file_paths['sellers'])
    product_category_name_translation = pd.read_csv(file_paths['product_category_name_translation'])

    logging.info("Merging datasets to create a single cohesive dataset...")
    
    # Merge datasets to create a single cohesive dataset
    orders_full = orders.merge(customers, on='customer_id', how='left')
    orders_full = orders_full.merge(order_items, on='order_id', how='left')
    orders_full = orders_full.merge(products, on='product_id', how='left')
    orders_full = orders_full.merge(sellers, on='seller_id', how='left')
    orders_full = orders_full.merge(order_reviews, on='order_id', how='left')
    orders_full = orders_full.merge(order_payments, on='order_id', how='left')
    orders_full = orders_full.merge(product_category_name_translation, on='product_category_name', how='left')

    # Feature Engineering
    logging.info("Performing feature engineering...")
    orders_full['order_purchase_timestamp'] = pd.to_datetime(orders_full['order_purchase_timestamp'])
    orders_full['purchase_day_of_week'] = orders_full['order_purchase_timestamp'].dt.dayofweek
    orders_full['purchase_hour'] = orders_full['order_purchase_timestamp'].dt.hour

    # Data Normalization
    logging.info("Normalizing data...")
    scaler = StandardScaler()
    numeric_features = ['price', 'freight_value', 'payment_value']
    orders_full[numeric_features] = scaler.fit_transform(orders_full[numeric_features])

    # Sentiment Analysis on Reviews
    logging.info("Performing sentiment analysis on reviews...")
    orders_full['review_sentiment'] = orders_full['review_comment_message'].fillna('').apply(analyze_sentiment)

    # Calculate average sentiment scores for products
    logging.info("Calculating average sentiment scores for products...")
    average_sentiment = orders_full.groupby('product_id')['review_sentiment'].mean().reset_index()
    average_sentiment.columns = ['product_id', 'avg_sentiment_score']

    # Merge average sentiment scores back into the main dataset
    orders_full = orders_full.merge(average_sentiment, on='product_id', how='left')

    logging.info("Data preprocessing complete.")
    return orders_full

# Function to perform sentiment analysis on reviews
def analyze_sentiment(review):
    analysis = TextBlob(review)
    return analysis.sentiment.polarity

# File paths dictionary
file_paths = {
    'customers': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_customers_dataset.csv',
    'order_items': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_order_items_dataset.csv',
    'order_payments': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_order_payments_dataset.csv',
    'order_reviews': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_order_reviews_dataset.csv',
    'orders': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_orders_dataset.csv',
    'products': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_products_dataset.csv',
    'sellers': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_sellers_dataset.csv',
    'product_category_name_translation': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/product_category_name_translation.csv'
}

# Load and preprocess data
orders_full = load_and_preprocess_data(file_paths)

# Location Analysis Agent
class LocationAnalysisAgent:
    def __init__(self, data):
        self.data = data

    def get_user_location(self, user_id):
        user_location = self.data[self.data['customer_unique_id'] == user_id]['customer_city'].iloc[0]
        logging.info(f"User location for user_id {user_id}: {user_location}")
        return user_location

    def get_popular_items_by_location(self, location):
        popular_items = self.data[self.data['customer_city'] == location]['product_id'].value_counts().head(10).index.tolist()
        logging.info(f"Popular items in location {location}: {popular_items}")
        return popular_items

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

# Explanation Agent
class ExplanationAgent:
    def __init__(self, location_items, history_items, collaborative_items, data):
        self.location_items = location_items
        self.history_items = history_items
        self.collaborative_items = collaborative_items
        self.data = data

    def generate_recommendations(self):
        # Integrate results to form a comprehensive recommendation list
        recommendations = {
            "location_based": self.location_items,
            "history_based": self.history_items,
            "collaborative_based": self.collaborative_items
        }
        logging.info(f"Generated recommendations: {recommendations}")
        return recommendations

    def generate_explanation(self, recommendations):
        location_explanation = ", ".join(self.get_product_names(recommendations['location_based']))
        history_explanation = ", ".join(self.get_product_names(recommendations['history_based']))
        collaborative_explanation = ", ".join(self.get_product_names(recommendations['collaborative_based']))

        explanation = f"Based on your location, we recommend: {location_explanation}. " \
                      f"Based on your order history and review sentiments, we recommend: {history_explanation}. " \
                      f"Other users similar to you bought: {collaborative_explanation}."
        logging.info(f"Generated explanation: {explanation}")
        return explanation

    def get_product_names(self, product_ids):
        product_names = self.data[self.data['product_id'].isin(product_ids)]['product_category_name_english'].unique().tolist()
        logging.info(f"Product names for product_ids {product_ids}: {product_names}")
        return product_names

# User ID for demonstration
user_id = '7c396fd4830fd04220f754e42b4e5bff'  # Replace with an actual user ID from the dataset

# Instantiate and run the location analysis agent
location_agent = LocationAnalysisAgent(orders_full)
user_location = location_agent.get_user_location(user_id)
popular_items_location = location_agent.get_popular_items_by_location(user_location)

# Instantiate and run the order history agent
order_history_agent = OrderHistoryAgent(orders_full)
user_order_history = order_history_agent.get_user_order_history(user_id)
similar_items = order_history_agent.get_similar_items(user_order_history)

# Instantiate and run the collaborative filtering agent
collaborative_filtering_agent = CollaborativeFilteringAgent(orders_full)
items_bought_by_similar_users = collaborative_filtering_agent.get_items_bought_by_similar_users(user_id)

# Instantiate and run the explanation agent
explanation_agent = ExplanationAgent(popular_items_location, similar_items, items_bought_by_similar_users, orders_full)
recommendations = explanation_agent.generate_recommendations()
explanation = explanation_agent.generate_explanation(recommendations)

# Print the explanation
print(explanation)

