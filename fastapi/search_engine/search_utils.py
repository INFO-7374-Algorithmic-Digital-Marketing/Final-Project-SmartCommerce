from fuzzywuzzy import fuzz
import pandas as pd
import logging

def get_search_results(query: str, orders_full: pd.DataFrame, threshold: int = 70) -> list:
    logging.info("Starting search with query: '%s'", query)
    
    # Convert the query to lowercase for case-insensitive search
    query = query.lower()
    logging.debug("Query converted to lowercase: '%s'", query)

    # Function to calculate the best fuzzy match score across multiple columns
    def fuzzy_match(row):
        category_score = fuzz.partial_ratio(query, str(row['product_category_name_english']).lower())
        title_score = fuzz.partial_ratio(query, str(row['title']).lower())
        description_score = fuzz.partial_ratio(query, str(row['shortDescription']).lower())
        max_score = max(category_score, title_score, description_score)
        
        logging.debug("Fuzzy scores - Category: %d, Title: %d, Description: %d, Max: %d", 
                      category_score, title_score, description_score, max_score)
        
        return max_score

    logging.info("Applying fuzzy matching to the DataFrame")
    # Apply the fuzzy match function and filter based on a threshold
    orders_full['match_score'] = orders_full.apply(fuzzy_match, axis=1)
    
    logging.info("Filtering results with match score >= %d", threshold)
    results = orders_full[orders_full['match_score'] >= threshold]
    
    logging.info("Found %d results matching the query", len(results))

    if results.empty:
        logging.warning("No results found for the query: '%s'", query)
    else:
        logging.info("Sorting results by match score")

    # Sort by match score
    sorted_results = results.sort_values(by='match_score', ascending=False)

    # Remove duplicates based on 'product_id'
    unique_results = sorted_results.drop_duplicates(subset='product_id')

    # Select the top 10 unique results
    top_results = unique_results.head(10)
    logging.info("Top 10 unique results selected")

    # Convert the results to the desired format
    search_results = []
    logging.info("Converting top results to the desired format")
    
    for index, item in top_results.iterrows():
        logging.debug("Processing product_id: %s with match_score: %d", item['product_id'], item['match_score'])
        search_results.append({
            "product_id": item['product_id'],
            "name": item['title'],
            "description": item['shortDescription'],
            "image_url": item['imageUrl'],
            "link": item['itemWebUrl'],
            "category": item['product_category_name_english'],
            "avg_sentiment_score": item['avg_sentiment_score'],
            "avg_price": item['target_price'],
            "summary": item['summary']
        })
    
    logging.info("Search completed, returning results")
    logging.info("Titles of top results: %s", [result['name'] for result in search_results])
    return search_results
