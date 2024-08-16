import os
from dotenv import load_dotenv
import requests
import base64
import json
import pandas as pd
from sqlalchemy import create_engine, text
from snowflake.sqlalchemy import URL
import logging
import sys
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

# Get the environment variables
CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")
PROCESSED_DATA_FOLDER_PATH = os.getenv("PROCESSED_DATA_FOLDER_PATH")

OAUTH_URL = 'https://api.ebay.com/identity/v1/oauth2/token'


# Encode the client ID and client secret
credentials = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8')).decode('utf-8')

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': f'Basic {credentials}'
}

data = {
    'grant_type': 'client_credentials',
    'scope': 'https://api.ebay.com/oauth/api_scope'
}

response = requests.post(OAUTH_URL, headers=headers, data=data)
if response.status_code == 200:
    access_token = response.json()['access_token']
else:
    print(f'Error: {response.status_code}')
    print(response.json())
    access_token = None

def get_item_details(item_id, access_token):
    endpoint = f'https://api.ebay.com/buy/browse/v1/item/{item_id}'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        print(response.json())
        return None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
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

def search_ebay_items_by_category_and_price(category_name, target_price, access_token):
    category_id = get_category_id(category_name, access_token)
    
    if not category_id:
        print(f"Category '{category_name}' not found.")
        return None
    
    print(f"Searching in category '{category_name}' with target price ${target_price:.2f}...")
    params = {
        'category_ids': category_id,
        'limit': 200  # Retrieve up to 200 items
    }
    
    items = search_ebay_items(params, access_token)
    if items:
        try:
            closest_item = min(items, key=lambda x: abs(float(x.get('price', {}).get('value', 0)) - target_price))
            details = get_item_details(closest_item['itemId'], access_token)
            return {
                'title': details.get('title', ''),
                'shortDescription': details.get('shortDescription', ''),
                'price': details['price']['value'] if 'price' in details else '',
                'imageUrl': details['image']['imageUrl'] if 'image' in details else '',
                'itemWebUrl': details.get('itemWebUrl', '')
            }
        except Exception as e:
            print(f"Error processing items for category '{category_name}': {str(e)}")
            return None
    
    print(f"No items found in category '{category_name}'.")
    return None

def get_category_id(category_name, access_token):
    # Define the endpoint and headers
    url = 'https://api.ebay.com/commerce/taxonomy/v1/category_tree/0/get_category_suggestions'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    
    # Define the query parameters
    params = {
        'q': category_name
    }
    
    # Make the GET request
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        categories = data.get('categorySuggestions')
        
        if categories:
            return categories[0]['category']['categoryId']  # Return the first matching category ID
    else:
        print(f"Error: {response.status_code}, {response.text}")
    
    return None

def search_ebay_items(params, access_token):
    endpoint = 'https://api.ebay.com/buy/browse/v1/item_summary/search'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    
    response = requests.get(endpoint, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get('itemSummaries', [])
        return items
    else:
        print(f'Error: {response.status_code}')
        print(response.json())
        return []

# Load the data
query = '''select 
    * 
from 
    top_products_with_price_summary
where 
    product_id in ( 
    select 
        product_id 
    from
        top_products_with_price_summary
    );'''

df = __run_query(query)

# Adding columns for the new data
df['title'] = ''
df['shortDescription'] = ''
df['price'] = ''
df['imageUrl'] = ''
df['itemWebUrl'] = ''

# Calculate target price
df['target_price'] = (df['min_price'] + df['max_price']) / 2

# List to keep track of categories that didn't work out
failed_categories = []

full_df = df.copy()

# Process each row in the DataFrame
if access_token:
    for index, row in tqdm(df.iterrows()):
        result = search_ebay_items_by_category_and_price(
            row['product_category_name_english'],
            row['target_price'],
            access_token
        )
        if result:
            df.at[index, 'title'] = result['title']
            df.at[index, 'shortDescription'] = result['shortDescription']
            df.at[index, 'price'] = result['price']
            df.at[index, 'imageUrl'] = result['imageUrl']
            df.at[index, 'itemWebUrl'] = result['itemWebUrl']
        else:
            failed_categories.append(row['product_category_name_english'])

df.to_csv(PROCESSED_DATA_FOLDER_PATH + 'generated_product_details.csv', index=False)

# Print the list of categories that didn't work out
print("\nCategories that failed to retrieve items:")
for category in failed_categories:
    print(category)