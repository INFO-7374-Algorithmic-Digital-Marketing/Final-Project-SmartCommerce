import pandas as pd
import logging
from textblob import TextBlob
import pandas as pd
from collections import Counter

RAW_DATA_FOLDER_PATH = '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/data_pipeline/data_files/raw/'
PROCESSED_DATA_FOLDER_PATH = '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/data_pipeline/data_files/processed/'

# Function to perform sentiment analysis on reviews
def analyze_sentiment(review):
    analysis = TextBlob(review)
    return analysis.sentiment.polarity

def aggregate_categories(df):
    user_categories = df.groupby('customer_id')['product_category_name_english'].agg(list).reset_index()
    user_categories['category_freq'] = user_categories['product_category_name_english'].apply(Counter)
    return user_categories

def get_top_5_categories(category_freq):
    return dict(sorted(category_freq.items(), key=lambda x: x[1], reverse=True)[:5])

persona_rules = {
    'sports_leisure': ['Athlete', 'Fitness Enthusiast'],
    'baby': ['Parent', 'Caregiver'],
    'toys': ['Parent', 'Child-oriented'],
    'books_general_interest': ['Bookworm', 'Intellectual'],
    'electronics': ['Tech Enthusiast', 'Gadget Lover'],
    'computers_accessories': ['Tech Professional', 'Gadget Lover'],
    'health_beauty': ['Beauty Enthusiast', 'Health-conscious'],
    'furniture_decor': ['Home Decorator', 'Interior Design Enthusiast'],
    'garden_tools': ['Gardener', 'Outdoor Enthusiast'],
    'pet_shop': ['Pet Owner', 'Animal Lover'],
    'fashion_bags_accessories': ['Fashion Enthusiast', 'Trendsetter'],
    'musical_instruments': ['Musician', 'Music Lover'],
    'food_drink': ['Foodie', 'Culinary Enthusiast'],
    'art': ['Artist', 'Art Collector'],
    'cine_photo': ['Photographer', 'Film Buff'],
    'watches_gifts': ['Gift Giver', 'Luxury Enthusiast'],
    'home_appliances': ['Home Chef', 'Domestic Enthusiast'],
    'auto': ['Car Enthusiast', 'DIY Mechanic'],
    'books_technical': ['Professional', 'Lifelong Learner'],
    'construction_tools_construction': ['DIY Enthusiast', 'Home Improver'],
    'stationery': ['Office Professional', 'Stationery Lover'],
    'cool_stuff': ['Trendsetter', 'Early Adopter'],
    'consoles_games': ['Gamer', 'Tech Enthusiast']
}

def assign_personas(category_freq):
    personas = set()
    for category, count in category_freq.items():
        if category in persona_rules:
            personas.update(persona_rules[category])
    return list(personas) if personas else ['General Consumer']

def create_persona_column(orders_full):
    # Aggregate categories
    user_categories = aggregate_categories(orders_full)
    
    # Get top 5 categories
    user_categories['top_5_categories'] = user_categories['category_freq'].apply(get_top_5_categories)
    
    # Assign personas based on top 5 categories
    user_categories['personas'] = user_categories['top_5_categories'].apply(assign_personas)
    
    # Join personas into a single string
    user_categories['persona_column'] = user_categories['personas'].apply(lambda x: ', '.join(x))
    
    # Merge back into main dataset
    orders_full_with_personas = orders_full.merge(user_categories[['customer_id', 'persona_column']], on='customer_id', how='left')
    
    # Fill NaN values with 'General Consumer'
    orders_full_with_personas['persona_column'] = orders_full_with_personas['persona_column'].fillna('General Consumer')
    
    return orders_full_with_personas


# Data Ingestion and Preprocessing Function
def create_orders_full():
    logging.info("Loading datasets...")

    # Load datasets
    customers = pd.read_csv(RAW_DATA_FOLDER_PATH + 'olist_customers_dataset.csv')
    order_items = pd.read_csv(RAW_DATA_FOLDER_PATH + 'olist_order_items_dataset.csv')
    order_payments = pd.read_csv(RAW_DATA_FOLDER_PATH + 'olist_order_payments_dataset.csv')
    order_reviews = pd.read_csv(RAW_DATA_FOLDER_PATH + 'olist_order_reviews_dataset.csv')
    orders = pd.read_csv(RAW_DATA_FOLDER_PATH + 'olist_orders_dataset.csv')
    products = pd.read_csv(RAW_DATA_FOLDER_PATH + 'olist_products_dataset.csv')
    sellers = pd.read_csv(RAW_DATA_FOLDER_PATH + 'olist_sellers_dataset.csv')
    product_category_name_translation = pd.read_csv(RAW_DATA_FOLDER_PATH + 'product_category_name_translation.csv')
    product_desc = pd.read_csv(PROCESSED_DATA_FOLDER_PATH + 'product_idf_descriptions.csv')
    review_summary = pd.read_csv(PROCESSED_DATA_FOLDER_PATH + 'top_1000_product_review_summaries.csv')
    
    logging.info("Merging datasets to create a single cohesive dataset...")
    # Merge datasets to create a single cohesive dataset
    orders_full = orders.merge(customers, on='customer_id', how='left')
    orders_full = orders_full.merge(order_items, on='order_id', how='left')
    orders_full = orders_full.merge(products, on='product_id', how='left')
    orders_full = orders_full.merge(sellers, on='seller_id', how='left')
    orders_full = orders_full.merge(order_reviews, on='order_id', how='left')
    orders_full = orders_full.merge(order_payments, on='order_id', how='left')
    orders_full = orders_full.merge(product_category_name_translation, on='product_category_name', how='left')
    orders_full = orders_full.merge(product_desc, on='product_id', how='left')
    orders_full = orders_full.merge(review_summary, on='product_id', how='left')
    
    # Feature Engineering
    logging.info("Performing feature engineering...")
    orders_full['order_purchase_timestamp'] = pd.to_datetime(orders_full['order_purchase_timestamp'])
    orders_full['purchase_day_of_week'] = orders_full['order_purchase_timestamp'].dt.dayofweek
    orders_full['purchase_hour'] = orders_full['order_purchase_timestamp'].dt.hour

    # Sentiment Analysis on Reviews
    logging.info("Performing sentiment analysis on reviews...")
    orders_full['review_sentiment'] = orders_full['summary'].fillna('').apply(analyze_sentiment)

    # Calculate average sentiment scores for products
    logging.info("Calculating average sentiment scores for products...")
    average_sentiment = orders_full.groupby('product_id')['review_sentiment'].mean().reset_index()
    average_sentiment.columns = ['product_id', 'avg_sentiment_score']

    # Merge average sentiment scores back into the main dataset
    orders_full = orders_full.merge(average_sentiment, on='product_id', how='left')
    orders_full = create_persona_column(orders_full)

    # Get top 1000 products by review count
    top_1000_product_ids = product_desc["product_id"].values

    # Filter orders to keep only those containing top 1000 products
    filtered_orders = orders_full[orders_full['product_id'].isin(top_1000_product_ids)]
    filtered_orders = filtered_orders.drop_duplicates()
    
    # Add a quantity column
    logging.info("Adding quantity column...")
    filtered_orders['quantity'] = 1
    filtered_orders['image_url'] = "https://picsum.photos/200/300"
    filtered_orders['link'] = "www.example.com"
    
    logging.info("Data preprocessing complete.")
    return filtered_orders


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    orders_full = create_orders_full()
    orders_full.to_csv(PROCESSED_DATA_FOLDER_PATH + 'orders_full.csv', index=False)
    logging.info(f"Data saved to {PROCESSED_DATA_FOLDER_PATH + 'orders_full.csv'}")