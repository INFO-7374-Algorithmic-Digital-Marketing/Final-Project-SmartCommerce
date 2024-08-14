import logging
from mlxtend.frequent_patterns import apriori, association_rules

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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


class MarketBasketAgent:
    def __init__(self, data, min_support=0.0001):
        self.data = data
        self.min_support = min_support
        self.rules = self.generate_rules()

    def generate_rules(self):
        logging.info("Loading and preprocessing data for Apriori algorithm...")
        data = self.data.copy()
        data = data.head(30000)
        data['quantity'] = 1

        item_freq = data['product_id'].value_counts()
        data = data[data['product_id'].isin(item_freq.index[item_freq >= 10])]

        basket = (data.groupby(['order_id', 'product_id'])['quantity']
                  .sum().unstack().reset_index().fillna(0).set_index('order_id'))
        basket_sets = basket.map(lambda x: 1 if x >= 1 else 0).astype(bool)

        logging.info("Generating frequent itemsets...")
        frequent_itemsets = apriori(basket_sets, min_support=self.min_support, use_colnames=True)
        frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))

        logging.info("Generating association rules...")
        rules = association_rules(frequent_itemsets, metric='confidence', min_threshold=0.01)
        high_confidence_rules = rules[rules['confidence'] >= 0.05]
        logging.info(f"High confidence rules: {high_confidence_rules}")

        return high_confidence_rules

    def recommend(self, user_order_history):
        recommendations = set()
        logging.info(f"User order history: {user_order_history}")
        for item in user_order_history:
            matching_rules = self.rules[self.rules['antecedents'].apply(lambda x: item in x)]
            for _, rule in matching_rules.iterrows():
                recommendations.update(rule['consequents'])
        logging.info(f"Apriori recommendations: {recommendations}")
        return [item for item in recommendations if item not in user_order_history]



