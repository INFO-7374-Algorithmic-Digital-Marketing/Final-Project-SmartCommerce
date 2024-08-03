import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float, DateTime, ForeignKey
from snowflake.sqlalchemy import URL
import os
from dotenv import load_dotenv
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Load environment variables
load_dotenv()

# Get Snowflake connection details from environment variables
def get_snowflake_engine():
    logger.info("Attempting to create Snowflake engine.")
    try:

        engine = create_engine(URL(
            user=os.getenv("MY_SNOWFLAKE_USER"),
            password=os.getenv("MY_SNOWFLAKE_PASSWORD"),
            account=os.getenv("MY_SNOWFLAKE_ACCOUNT"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            role=os.getenv("SNOWFLAKE_ROLE"),
        ))
        logger.info("Snowflake engine created successfully.")
        return engine
    except Exception as e:
        logger.error("Error creating Snowflake engine: %s", e)
        sys.exit(1)

# Define table schemas
def define_tables(metadata):
    logger.info("Defining tables.")
    try:
        Table('Customers', metadata,
            Column('customer_id', String, primary_key=True),
            Column('customer_unique_id', String),
            Column('customer_zip_code_prefix', Integer),
            Column('customer_city', String),
            Column('customer_state', String)
        )
        logger.info("Table 'Customers' defined.")

        Table('Geolocations', metadata,
            Column('geolocation_zip_code_prefix', Integer),
            Column('geolocation_lat', Float),
            Column('geolocation_lng', Float),
            Column('geolocation_city', String),
            Column('geolocation_state', String)
        )
        logger.info("Table 'Geolocations' defined.")

        Table('Order_Items', metadata,
            Column('order_id', String),
            Column('order_item_id', Integer),
            Column('product_id', String),
            Column('seller_id', String),
            Column('shipping_limit_date', DateTime),
            Column('price', Float),
            Column('freight_value', Float)
        )
        logger.info("Table 'Order_Items' defined.")

        Table('Payments', metadata,
            Column('order_id', String),
            Column('payment_sequential', Integer),
            Column('payment_type', String),
            Column('payment_installments', Integer),
            Column('payment_value', Float)
        )
        logger.info("Table 'Payments' defined.")

        Table('Reviews', metadata,
            Column('review_id', String, primary_key=True),
            Column('order_id', String),
            Column('review_score', Integer),
            Column('review_comment_title', String),
            Column('review_comment_message', String),
            Column('review_creation_date', DateTime),
            Column('review_answer_timestamp', DateTime)
        )
        logger.info("Table 'Reviews' defined.")

        Table('Orders', metadata,
            Column('order_id', String, primary_key=True),
            Column('customer_id', String),
            Column('order_status', String),
            Column('order_purchase_timestamp', DateTime),
            Column('order_approved_at', DateTime),
            Column('order_delivered_carrier_date', DateTime),
            Column('order_delivered_customer_date', DateTime),
            Column('order_estimated_delivery_date', DateTime)
        )
        logger.info("Table 'Orders' defined.")

        Table('Products', metadata,
            Column('product_id', String, primary_key=True),
            Column('product_category_name', String),
            Column('product_name_length', Integer),
            Column('product_description_length', Integer),
            Column('product_photos_qty', Integer),
            Column('product_weight_g', Float),
            Column('product_length_cm', Float),
            Column('product_height_cm', Float),
            Column('product_width_cm', Float)
        )
        logger.info("Table 'Products' defined.")

        Table('Sellers', metadata,
            Column('seller_id', String, primary_key=True),
            Column('seller_zip_code_prefix', Integer),
            Column('seller_city', String),
            Column('seller_state', String)
        )
        logger.info("Table 'Sellers' defined.")

        Table('Product_Category_Translation', metadata,
            Column('product_category_name', String, primary_key=True),
            Column('product_category_name_english', String)
        )
        logger.info("Table 'Product_Category_Translation' defined.")
    except Exception as e:
        logger.error("Error defining tables: %s", e)
        sys.exit(1)

# Create tables in Snowflake
def create_tables(engine, metadata):
    logger.info("Attempting to create tables in Snowflake.")
    try:
        metadata.create_all(engine)
        logger.info("Tables created successfully in Snowflake.")
    except Exception as e:
        logger.error("Error creating tables in Snowflake: %s", e)
        sys.exit(1)

# Insert data into tables
def insert_data(df, table, engine):
    logger.info("Inserting data into table '%s'.", table.name)
    try:
        df.to_sql(table.name, con=engine, index=False, if_exists='append')
        logger.info("Data inserted into '%s' table successfully.", table.name)
    except Exception as e:
        logger.error("Error inserting data into '%s' table: %s", table.name, e)
        sys.exit(1)

# Load CSV files into DataFrames
def load_data(file_path):
    logger.info("Loading data from %s", file_path)
    try:
        df = pd.read_csv(file_path)
        logger.info("Data loaded successfully from %s", file_path)
        return df
    except Exception as e:
        logger.error("Error loading data from %s: %s", file_path, e)
        sys.exit(1)

# Main function
def main():
    # Establish Snowflake connection
    engine = get_snowflake_engine()
    metadata = MetaData()

    # Define and create tables
    define_tables(metadata)
    create_tables(engine, metadata)

    # File paths
    files = {
        'Customers': 'data_files/olist_customers_dataset.csv',
        'Geolocations': 'data_files/olist_geolocation_dataset.csv',
        'Order_Items': 'data_files/olist_order_items_dataset.csv',
        'Payments': 'data_files/olist_order_payments_dataset.csv',
        'Reviews': 'data_files/olist_order_reviews_dataset.csv',
        'Orders': 'data_files/olist_orders_dataset.csv',
        'Products': 'data_files/olist_products_dataset.csv',
        'Sellers': 'data_files/olist_sellers_dataset.csv',
        'Product_Category_Translation': 'data_files/product_category_name_translation.csv'
    }

    # Insert data into Snowflake tables
    for table_name, file_path in files.items():
        df = load_data(file_path)
        insert_data(df, metadata.tables[table_name], engine)

if __name__ == "__main__":
    main()
