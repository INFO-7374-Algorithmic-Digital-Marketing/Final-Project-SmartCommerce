import database as db

#Query to get the churn flag for a customer
def get_churn_flag(customer_id):
    sql_query = f'''select churn_flag from "Customers" where customer_id = '{customer_id}';'''
    return db.__run_query(sql_query)

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
    return db.__run_query(sql_query)

#Function to get the price for product according to churn flag
def get_price(product_id, churn_flag):
    min_max_price = __get_min_max_price(product_id)
    if churn_flag:
        return min_max_price['min_price'][0]
    else:
        return min_max_price['max_price'][0]

customer_id = "00012a2ce6f8dcda20d059ce98491703"
get_price("4244733e06e7ecb4970a6e2683c13e61", get_churn_flag(customer_id)['churn_flag'][0])