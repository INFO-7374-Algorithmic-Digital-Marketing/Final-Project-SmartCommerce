-- Switch to the ACCOUNTADMIN role
USE ROLE ACCOUNTADMIN;

-- Create a new role and grant necessary privileges
CREATE ROLE final_project_role;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE final_project_role;
GRANT CREATE WAREHOUSE ON ACCOUNT TO ROLE final_project_role;
GRANT CREATE INTEGRATION ON ACCOUNT TO ROLE final_project_role;

-- Create a new database and warehouse, and assign ownership
CREATE DATABASE IF NOT EXISTS final_project_db;
GRANT OWNERSHIP ON DATABASE final_project_db TO ROLE final_project_role COPY CURRENT GRANTS;

CREATE OR REPLACE WAREHOUSE final_project_warehouse 
  WITH WAREHOUSE_SIZE = 'SMALL';
GRANT USAGE ON WAREHOUSE final_project_warehouse TO ROLE final_project_role;

-- Grant additional privileges to the role
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE final_project_role;
GRANT CREATE COMPUTE POOL ON ACCOUNT TO ROLE final_project_role;

-- Create a compute pool and grant usage and monitoring privileges
CREATE COMPUTE POOL final_project_compute_pool
  MIN_NODES = 1
  MAX_NODES = 2
  INSTANCE_FAMILY = CPU_X64_XS;
GRANT USAGE, MONITOR ON COMPUTE POOL final_project_compute_pool TO ROLE final_project_role;

-- Assign the role to a user
GRANT ROLE final_project_role TO USER DEVESH12345;

-- Switch to the new role and set up the environment
USE ROLE final_project_role;
USE DATABASE final_project_db;
USE WAREHOUSE final_project_warehouse;

-- Create schema, image repository, and stage
CREATE SCHEMA IF NOT EXISTS final_project_schema;
CREATE IMAGE REPOSITORY IF NOT EXISTS final_project_repository;
CREATE STAGE IF NOT EXISTS final_project_stage
  DIRECTORY = (ENABLE = TRUE);

-- Create a network rule and secret for external access integration
CREATE OR REPLACE NETWORK RULE FINAL_PROJECT_NETWORK_RULE
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('0.0.0.0');

CREATE OR REPLACE SECRET FINAL_PROJECT_API_KEY
  TYPE = GENERIC_STRING
  SECRET_STRING = 'sk-proj-NewSecretKeyForFinalProject';

-- Create an external access integration
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION FINAL_PROJECT_INTEGRATION
  ALLOWED_NETWORK_RULES = (FINAL_PROJECT_NETWORK_RULE)
  ALLOWED_AUTHENTICATION_SECRETS = (FINAL_PROJECT_API_KEY)
  ENABLED = TRUE;

-- Show resources (compute pools, warehouses, image repositories, and stages)
SHOW COMPUTE POOLS;
SHOW WAREHOUSES;
SHOW IMAGE REPOSITORIES;
SHOW STAGES;
DESCRIBE COMPUTE POOL final_project_compute_pool;
SHOW IMAGES IN IMAGE REPOSITORY final_project_repository;

-- Create a service in the compute pool
CREATE SERVICE final_service
  IN COMPUTE POOL final_project_compute_pool
  FROM SPECIFICATION $$
    spec:
      containers:
      - name: final-container
        image: /final_project_db/final_project_schema/final_project_repository/final_image:v2
        env:
          SERVER_PORT: 8000
        readinessProbe:
          port: 8000
          path: /docs
      endpoints:
      - name: finalendpoint
        port: 8000
        public: true
  $$
  EXTERNAL_ACCESS_INTEGRATIONS = (FINAL_PROJECT_INTEGRATION)
  MIN_INSTANCES = 1
  MAX_INSTANCES = 2;

-- Create a UDF linked to the service endpoint
CREATE FUNCTION product_search(user_id VARCHAR, query VARCHAR)
  RETURNS VARCHAR
  SERVICE = final_service
  ENDPOINT = finalendpoint
  AS '/product_search_udf';

-- Product Search UDF
CREATE FUNCTION product_search(user_id VARCHAR, query VARCHAR)
  RETURNS VARCHAR
  SERVICE = final_service
  ENDPOINT = finalendpoint
  AS '/product_search_udf';

-- Authentication UDF
CREATE FUNCTION authenticate(user_id VARCHAR, password VARCHAR)
  RETURNS VARCHAR
  SERVICE = final_service
  ENDPOINT = finalendpoint
  AS '/authenticate_udf';

-- Context-Aware Recommendations UDF
CREATE FUNCTION context_aware_recommendations(user_id VARCHAR)
  RETURNS VARCHAR
  SERVICE = final_service
  ENDPOINT = finalendpoint
  AS '/context_aware_recommendations_udf';

-- Content Filter Recommendations UDF
CREATE FUNCTION content_filter_recommendations(user_id VARCHAR)
  RETURNS VARCHAR
  SERVICE = final_service
  ENDPOINT = finalendpoint
  AS '/content_filter_recommendations_udf';

-- Collaborative Filtering Recommendations UDF
CREATE FUNCTION collaborative_filtering_recommendations(user_id VARCHAR)
  RETURNS VARCHAR
  SERVICE = final_service
  ENDPOINT = finalendpoint
  AS '/collaborative_filtering_recommendations_udf';

-- Market Basket Recommendations UDF
CREATE FUNCTION market_basket_recommendations(user_id VARCHAR)
  RETURNS VARCHAR
  SERVICE = final_service
  ENDPOINT = finalendpoint
  AS '/market_basket_recommendations_udf';

-- Top Selling Products UDF
CREATE FUNCTION top_selling_products(user_id VARCHAR)
  RETURNS VARCHAR
  SERVICE = final_service
  ENDPOINT = finalendpoint
  AS '/top_selling_products_udf';

-- Worst Performing Products UDF
CREATE FUNCTION worst_performing_products(user_id VARCHAR)
  RETURNS VARCHAR
  SERVICE = final_service
  ENDPOINT = finalendpoint
  AS '/worst_performing_products_udf';

-- Competitor Analysis UDF
CREATE FUNCTION competitor_analysis(user_id VARCHAR)
  RETURNS VARCHAR
  SERVICE = final_service
  ENDPOINT = finalendpoint
  AS '/competitor_analysis_udf';

-- Customer Targeting UDF
CREATE FUNCTION customer_targeting(user_id VARCHAR)
  RETURNS VARCHAR
  SERVICE = final_service
  ENDPOINT = finalendpoint
  AS '/customer_targeting_udf';

-- Supply Chain Optimization UDF
CREATE FUNCTION supply_chain_optimization(user_id VARCHAR)
  RETURNS VARCHAR
  SERVICE = final_service
  ENDPOINT = finalendpoint
  AS '/supply_chain_optimization_udf';
  
-- Show and describe the service
SHOW SERVICES;
SELECT SYSTEM$GET_SERVICE_STATUS('final_service');
DESCRIBE SERVICE final_service;

-- Test the UDF
SELECT product_search('548a09978548d2e347d494793e34c797','gold watch');

-- Get service logs
SELECT SYSTEM$GET_SERVICE_LOGS('final_service', '0', 'final-container', 1000);
    
-- Show endpoints in the service
SHOW ENDPOINTS IN SERVICE final_service;

-- Cleanup (uncomment when ready to remove everything)
-- DROP SERVICE final_service;
-- USE ROLE ACCOUNTADMIN;
-- ALTER COMPUTE POOL final_project_compute_pool STOP ALL;
-- DROP COMPUTE POOL final_project_compute_pool;
-- USE ROLE final_project_role;
-- DROP IMAGE REPOSITORY final_project_repository;
-- DROP STAGE final_project_stage;
-- DROP DATABASE final_project_db;
-- USE ROLE ACCOUNTADMIN;
-- DROP ROLE final_project_role;
