from sklearn.preprocessing import StandardScaler
import pandas as pd
from textblob import TextBlob
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# File paths dictionary
file_paths = {
    'customers': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_customers_dataset.csv',
    'order_items': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_order_items_dataset.csv',
    'order_payments': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_order_payments_dataset.csv',
    'order_reviews': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_order_reviews_dataset.csv',
    'orders': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_orders_dataset.csv',
    'products': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_products_dataset.csv',
    'sellers': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_sellers_dataset.csv',
    'product_category_name_translation': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/product_category_name_translation.csv',
    'product_desc':'/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/backend/Rec_sys/notebooks/product_idf_descriptions.csv'
}

# Function to perform sentiment analysis on reviews
def analyze_sentiment(review):
    analysis = TextBlob(review)
    return analysis.sentiment.polarity

# Data Ingestion and Preprocessing Function
def load_and_preprocess_data():
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
    product_desc = pd.read_csv(file_paths['product_desc'])

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
    # filtered_orders = orders_full
    # Count the number of reviews per product
    # review_counts = orders_full.groupby('product_id')['review_id'].count().sort_values(ascending=False)

    # Get top 1000 products by review count
    top_1000_product_ids = product_desc["product_id"].values

    # Filter orders to keep only those containing top 1000 products
    filtered_orders = orders_full[orders_full['product_id'].isin(top_1000_product_ids)]

    # Filter customers to keep only those who placed orders containing top 1000 products
    filtered_orders = filtered_orders.drop_duplicates()
    # import pdb; pdb.set_trace()

    logging.info("Datasets merged into a single dataframe based on top 1000 products.")
    
    # Add a quantity column
    logging.info("Adding quantity column...")
    filtered_orders['quantity'] = 1
    
    logging.info("Data preprocessing complete.")
    return filtered_orders

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

def apriori_recommendation_system(min_support=0.0001):
    # Load data
    # import pdb; pdb.set_trace()
    logging.info("Loading order items dataset...")
    data = pd.read_csv(file_paths["order_items"])
    data = data.head(40000)

    # Append Quantity column
    data['quantity'] = 1
    
    logging.info("Generating association rules using Apriori algorithm...")
    # Filter products purchased at least 10 times
    item_freq = data['product_id'].value_counts()
    data = data[data['product_id'].isin(item_freq.index[item_freq >= 10])]
    
    logging.info("Creating basket and generating frequent itemsets...")
    # Create basket
    basket = (data.groupby(['order_id', 'product_id'])['quantity']
              .sum().unstack().reset_index().fillna(0).set_index('order_id'))
    logging.info("Basket created.")
    
    logging.info("Encoding units for Apriori...")
    # Encode units for apriori
    basket_sets = basket.map(lambda x: 1 if x >= 1 else 0)
    logging.info("Units encoded.")
    
    # Generate frequent itemsets
    logging.info("Generating frequent itemsets...")
    frequent_itemsets = apriori(basket_sets, min_support=min_support, use_colnames=True)
    frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))
    logging.info("Frequent itemsets generated.")

    # Generate association rules
    logging.info("Generating association rules...")
    rules = association_rules(frequent_itemsets, metric = 'confidence', min_threshold = 0.01)
    logging.info("Association rules generated as follows:")
    print(rules)    
    
    # Filter rules with confidence >= 0.50
    high_confidence_rules = rules[rules['confidence'] >= 0.05]
    logging.info("High confidence rules generated as follows:")
    # Save to CSV
    return high_confidence_rules
