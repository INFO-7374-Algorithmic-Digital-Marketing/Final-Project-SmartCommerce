# SmartCommerce: Multi-Agent Marketing Intelligence

## Live Application Links

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)]()

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)]()

[![codelabs](https://img.shields.io/badge/codelabs-4285F4?style=for-the-badge&logo=codelabs&logoColor=white)]()

## Problem Statement
Businesses face critical challenges in engaging with customers and optimizing operations. Key challenges include predicting customer preferences, managing churn, and providing effective support. Addressing these issues is crucial to maintaining customer satisfaction, reducing churn rates, and improving operational efficiency.

## Project Goals
- Develop a multi-agent system to handle personalized product recommendations, churn prediction, and automated customer service.
- Implement a personalized recommendation system using collaborative and content-based filtering.
- Develop churn prediction models and retention strategies.
- Create an automated customer service bot to handle inquiries efficiently.
- Deploy the system using FastAPI, Docker, and Snowpark container services.

## Technologies Used
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)
[![FastAPI](https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)](https://www.python.org/)

## Data Sources
- olist_orders_dataset.csv
- olist_order_items_dataset.csv
- olist_order_payments_dataset.csv
- olist_order_reviews_dataset.csv
- olist_order_customer_dataset.csv
- olist_sellers_dataset.csv
- olist_products_dataset.csv
- olist_geolocation_dataset.csv
- product_category_name_translation.csv

## Pre-requisites
- Knowledge of Python and data analysis libraries (Pandas, NumPy).
- Understanding of machine learning concepts and algorithms.
- Familiarity with web frameworks (FastAPI) and containerization (Docker).
- Access to Snowflake for data storage and querying.

## Project Structure

```
/my_streamlit_app/
│
├── /app/
│   ├── main.py                # Entry point for the Streamlit app
│   ├── /pages/
│   │   ├── recommendation.py  # Recommendation system page
│   │   ├── chatbot.py         # Customer service chatbot page
│   │   └── seller_dashboard.py# Seller dashboard page
│   ├── /components/
│   │   ├── header.py          # Common header component
│   │   ├── footer.py          # Common footer component
│   │   └── sidebar.py         # Sidebar for navigation
│   ├── /utils/
│   │   ├── auth.py            # User authentication and identification logic
│   │   ├── api_calls.py       # Functions for calling FastAPI endpoints
│   │   └── data_processing.py # Data processing functions for UI components
│   └── /styles/
│       └── app_styles.css     # Custom CSS for styling the Streamlit app
│
├── /api/
│   ├── main.py                # Entry point for the FastAPI server
│   ├── /routes/
│   │   ├── recommendation.py  # API routes for recommendation system
│   │   ├── chatbot.py         # API routes for customer service chatbot
│   │   └── seller.py          # API routes for seller dashboard
│   ├── /services/
│   │   ├── recommendation_service.py # Business logic for recommendations
│   │   ├── chatbot_service.py        # Business logic for chatbot
│   │   └── seller_service.py         # Business logic for seller dashboard
│   └── /models/
│       ├── user.py            # Database models for user information
│       └── product.py         # Database models for products/recommendations
│
├── /tests/
│   ├── /unit/
│   │   ├── test_auth.py        # Unit tests for authentication
│   │   ├── test_recommendation.py # Unit tests for recommendation system
│   │   └── test_chatbot.py     # Unit tests for chatbot
│   └── /integration/
│       ├── test_endpoints.py   # Integration tests for API endpoints
│       └── test_user_flows.py  # Integration tests for user flows in the app
│
├── Dockerfile                  # Dockerfile for containerizing the application
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

*You can generate the project tree using following tools*
*[Project Tree Generator](https://woochanleee.github.io/project-tree-generator)*
*[Generate from terminal](https://www.geeksforgeeks.org/tree-command-unixlinux/)*

## Empty .env file
```
OPENAI_API_KEY=""
GROQ_API_KEY=""
MY_SNOWFLAKE_ACCOUNT=""
MY_SNOWFLAKE_USER=""
MY_SNOWFLAKE_PASSWORD=""
SNOWFLAKE_ROLE=""
SNOWFLAKE_DATABASE=""
SNOWFLAKE_SCHEMA=""
SNOWFLAKE_WAREHOUSE=""
```

## Data Pipeline

1. Run the 01_database.py script to create tables in Snowflake and load data from CSV files.

## How to run Application locally

1. **Clone the repository:**
 ```bash
 git clone https://github.com/your-repo-url.git
 cd your-repo-url
 ```
   
2. Set up virtual environment and install dependencies:

```bash
conda create --name smartcommerce python=3.10
conda activate smartcommerce
pip install -r requirements.txt
```

3. Run Streamlit application:

```bash
cd streamlit
streamlit run main.py
```

4. Run FastAPI application:

```bash
cd fastapi
uvicorn main:app --reload
```

5. Build and run Docker containers:

```bash
docker-compose up --build
```

## References
- https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data
     
## Learning Outcomes
- Understanding of multi-agent systems in e-commerce.
- Skills in data preprocessing, machine learning, and recommendation systems.
- Experience in deploying web applications using FastAPI and Docker.
- Knowledge of Snowflake for data storage and querying.

## Team Information and Contribution 
WE ATTEST THAT WE HAVEN'T USED ANY OTHER STUDENTS' WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK 

Name | Contribution %| Contributions |
--- |--- | --- |
Devesh Surve | 50% | |
Snehil Aryan | 50% | |
