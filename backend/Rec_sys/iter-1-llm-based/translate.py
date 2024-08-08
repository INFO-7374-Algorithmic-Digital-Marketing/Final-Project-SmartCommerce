import openai
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'

class ReviewSummarizer:
    def __init__(self, data):
        self.data = data

    def summarize_reviews(self, reviews):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant that translates Brazilian Portuguese reviews to English and "
                            "summarizes them into a single paragraph in English."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Translate and summarize the following reviews: {reviews}"
                    }
                ],
                max_tokens=150
            )
            summary = response.choices[0].message['content'].strip()
            return summary
        except Exception as e:
            logging.error(f"Error summarizing reviews: {e}")
            return None

    def process_reviews(self):
        logging.info("Translating and summarizing reviews...")

        # Group reviews by product_id
        grouped_reviews = self.data.groupby('product_id')['review_comment_message'].apply(lambda x: ' '.join(x.dropna()))

        summaries = []
        for product_id, reviews in grouped_reviews.items():
            summary = self.summarize_reviews(reviews)
            summaries.append({'product_id': product_id, 'summary': summary})

        # Convert summaries to DataFrame
        summaries_df = pd.DataFrame(summaries)

        # Store summaries in a CSV file
        summaries_df.to_csv('product_reviews_summary.csv', index=False)
        logging.info("Summaries saved to product_reviews_summary.csv")

# Example usage
file_paths = {
    'order_reviews': '/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/project_proposal/data/olist_order_reviews_dataset.csv'
}

# Load order reviews dataset
order_reviews = pd.read_csv(file_paths['order_reviews'])

# Instantiate and run the review summarizer
review_summarizer = ReviewSummarizer(order_reviews)
review_summarizer.process_reviews()
