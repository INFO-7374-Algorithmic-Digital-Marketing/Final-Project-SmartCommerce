from sqlalchemy import create_engine, text
import pandas as pd
import os
from dotenv import load_dotenv
import logging
from snowflake.sqlalchemy import URL

# Load environment variables from a .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Create the Snowflake engine
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
except Exception as e:
    logger.error(f"Error creating Snowflake engine: {e}")
    raise

def show_tables(connection):
    logger.info("Fetching list of tables in the schema.")
    try:
        query = text("SHOW TABLES IN SCHEMA SMARTCOMMERCE.PUBLIC;")
        result = connection.execute(query).fetchall()
        for row in result:
            logger.info(f"Table: {row[1]}")
    except Exception as e:
        logger.error(f"Error fetching tables: {e}")

def check_table_exists(connection, table_name):
    logger.info(f"Checking if table {table_name} exists.")
    try:
        query = text(f"SHOW TABLES LIKE '{table_name}';")
        result = connection.execute(query).fetchall()
        table_exists = len(result) > 0
        logger.info(f"Table {table_name} exists: {table_exists}")
        return table_exists
    except Exception as e:
        logger.error(f"Error checking table existence: {e}")
        return False

def run_query(query):
    try:
        connection = engine.connect()
        logger.info("Connected to Snowflake")
        
        # Verify current database and schema
        current_db_schema = connection.execute(text("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA();")).fetchall()
        logger.info(f"Current Database and Schema: {current_db_schema}")
        
        # Parameterized query with double quotes around the table name
        query = text(query)
        logger.info(f"Executing query: {query}")
        result = connection.execute(query).fetchall()
        
        try:
            logger.info("Query executed successfully and results fetched")
            return result
        except Exception as e:
            logger.error(f"Error converting query results to DataFrame: {e}")
            return None
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return None
    finally:
        connection.close()
        logger.info("Connection closed")

# Test the run_query function
result = run_query('SELECT * FROM "Customers" LIMIT 5;')
print(result)
