# SmartCommerce: Multi-Agent Marketing Intelligence

## Live Application Links

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](35.231.130.157:8501)

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)](35.231.130.157:8000/docs)

[![codelabs](https://img.shields.io/badge/codelabs-4285F4?style=for-the-badge&logo=codelabs&logoColor=white)](https://codelabs-preview.appspot.com/?file_id=1N5TJkbmNsmNCn_fURhboz4v4yyjw-MnuAncG03n9IO8#0)

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
.
├── Makefile
├── README.md
├── data_pipeline
│   ├── 01_eda.ipynb
│   ├── 02_feature_engineering.py
│   ├── 03_upload_to_snowflake.py
│   └── data_files
│       ├── processed
│       │   ├── orders_full.csv
│       │   ├── product_avg_price.csv
│       │   ├── product_idf_descriptions.csv
│       │   └── top_1000_product_review_summaries.csv
│       └── raw
│           ├── olist_customers_dataset.csv
│           ├── olist_geolocation_dataset.csv
│           ├── olist_order_items_dataset.csv
│           ├── olist_order_payments_dataset.csv
│           ├── olist_order_reviews_dataset.csv
│           ├── olist_orders_dataset.csv
│           ├── olist_products_dataset.csv
│           ├── olist_sellers_dataset.csv
│           └── product_category_name_translation.csv
├── diagrams
│   ├── Architecture.drawio
│   ├── Architecture.drawio.png
│   ├── iter_0.png
│   └── iter_1.png
├── fastapi
│   ├── main.py
│   └── recommendation_systems
│       ├── collaborative_filter.py
│       ├── content_filter.py
│       ├── contextual_filter.py
│       └── market_basket_analysis.py
├── project_proposal
│   ├── 01_EDA.ipynb
│   ├── 02_Content_Based_Filtering_RecSys.ipynb
│   ├── 03_Collaborative_Filtering_RecSys copy.ipynb
│   ├── 04_Agentic_RecSys.ipynb
│   ├── 05_Churn_Modelling.ipynb
│   ├── 06_Agentic_User_Behaviour_Email.ipynb
│   ├── 07_Agentic_Customer_Service_Bot.ipynb
│   └── data
│       ├── olist_customers_dataset.csv
│       ├── olist_geolocation_dataset.csv
│       ├── olist_order_items_dataset.csv
│       ├── olist_order_payments_dataset.csv
│       ├── olist_order_reviews_dataset.csv
│       ├── olist_orders_dataset.csv
│       ├── olist_products_dataset.csv
│       ├── olist_sellers_dataset.csv
│       └── product_category_name_translation.csv
├── requirements.txt
├── streamlit
│   └── main.py
└── tests
    ├── integration
    └── unit
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
