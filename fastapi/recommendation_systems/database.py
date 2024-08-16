import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float, DateTime, ForeignKey, text
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

def __run_query(query, engine = get_snowflake_engine(), update = False):
    connection = engine.connect()
    logging.info("Connected to Snowflake")
    
    try:
        # connection.execute(text("USE ASG_4_P2.PUBLIC;"))
        # logging.info("Switched to ASG_4_P2.PUBLIC")
        
        # Make parameterized query such that no DELETE / UPDATE queries can be run
        query = text(query)
        logger.info(f"Executing query: {query}")
        result = connection.execute(query).fetchall()
        if update:
            connection.commit()
            logging.info("Transaction committed.")
        try:
            result_df = pd.DataFrame(result)
            logging.info("Query executed successfully and results fetched")
            return result_df
        except Exception as e:
            logging.error(f"Error converting query results to DataFrame: {e}")
            return None
    except Exception as e:
        logging.error(f"Error executing query: {e}")
        return None
    finally:
        connection.close()
        logging.info("Connection closed")

def update_churn_flag(churned_cust_ids, non_churned_customer_ids):
    update_query_churn = f"""
    UPDATE "Customers"
    SET churn_flag = TRUE
    WHERE customer_id IN ({', '.join(f"'{customer_id}'" for customer_id in churned_cust_ids)});
    """
    __run_query(update_query_churn, update=True)
    
    update_query_non_churn = f"""
    UPDATE "Customers"
    SET churn_flag = TRUE
    WHERE customer_id IN ({', '.join(f"'{customer_id}'" for customer_id in non_churned_customer_ids)});
    """
    __run_query(update_query_non_churn, update=True)

#Query to get the churn flag for a customer
def get_churn_flag(customer_id):
    sql_query = f'''select churn_flag from "Customers" where customer_id = '{customer_id}';'''
    return __run_query(sql_query)

#Query to get the min and max price of a product
def __get_min_max_price(product_id):
    sql_query = f'''SELECT 
        MAX(price) AS max_price,
        MIN(price) AS min_price
    FROM 
        "Order_Items"
    GROUP BY 
        product_id
    having product_id = '{product_id}';'''
    return __run_query(sql_query)

#Function to get the price for product according to churn flag
def get_price(product_id, churn_flag):
    min_max_price = __get_min_max_price(product_id)
    if churn_flag:
        return min_max_price['min_price'][0]
    else:
        return min_max_price['max_price'][0]

