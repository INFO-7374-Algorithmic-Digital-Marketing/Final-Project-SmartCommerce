from dotenv import load_dotenv
import logging
from llama_agents import (
    AgentService, ControlPlaneServer, SimpleMessageQueue, LocalLauncher, AgentOrchestrator
)
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize user profile
user_profile = {"name": "User1", "location": "New York", "feedback": []}

# Function to simulate getting recommendations
def get_recommendations(user_profile) -> dict:
    logger.info(f"Getting recommendations for user {user_profile['name']} in {user_profile['location']}")
    location = user_profile.get('location', 'Unknown')
    product_type = "general"  # This can be determined based on user profile

    try:
        geospatial_trends = launcher.launch_single(
            f"Retrieve geospatial trends for {product_type} products in {location}. Provide relevant market data and insights."
        )
        logger.info(f"Geospatial trends: {geospatial_trends}")
    except Exception as e:
        logger.error(f"Error retrieving geospatial trends: {e}")
        geospatial_trends = "Error retrieving geospatial trends."

    base_recommendations = ["Item1", "Item2", "Item3"]  # Your original recommendation logic

    final_recommendations = []
    for item in base_recommendations:
        try:
            logger.info(f"Processing recommendation for {item}")
            reviews = launcher.launch_single(
                f"Analyze reviews for product {item}. Provide key insights and overall sentiment analysis."
            )
            logger.info(f"Reviews: {reviews}")
            explanation = launcher.launch_single(
                f"Generate a personalized explanation for recommending product {item} to user {user_profile['name']} based on their profile and preferences."
            )
            logger.info(f"Explanation: {explanation}")
            final_recommendations.append({
                "item": item,
                "reviews": reviews,
                "explanation": explanation
            })
        except Exception as e:
            logger.error(f"Error processing recommendation for {item}: {e}")
            final_recommendations.append({
                "item": item,
                "reviews": "Error retrieving reviews.",
                "explanation": "Error generating explanation."
            })

    return {
        "recommendations": final_recommendations,
        "geospatial_trends": geospatial_trends
    }

# Function to simulate updating user profile
def update_profile(user_profile, feedback) -> dict:
    """Update the user profile based on feedback."""
    logger.info(f"Updating profile for user {user_profile['name']} with feedback: {feedback}")
    try:
        user_profile['feedback'].append(feedback)
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
    return user_profile

# Function to fetch geospatial trends
def get_geospatial_trends(location, product_type):
    logger.info(f"Fetching geospatial trends for {product_type} in {location}")
    return f"Trends for {product_type} in {location}: Trend1, Trend2, Trend3"

# Function to analyze reviews
def analyze_reviews(product_id):
    logger.info(f"Analyzing reviews for product {product_id}")
    return f"Insights for product {product_id}: Insight1, Insight2, Insight3"

# Function to generate explanations
def generate_explanation(recommendation, user_profile):
    logger.info(f"Generating explanation for recommendation {recommendation} for user {user_profile['name']}")
    return f"Explanation for recommendation {recommendation} for user {user_profile['name']}: ..."

# Create tools
recommendation_tool = FunctionTool.from_defaults(fn=lambda: get_recommendations(user_profile), name="get_recommendations")
update_profile_tool = FunctionTool.from_defaults(fn=lambda feedback: update_profile(user_profile, feedback), name="update_profile")
geospatial_tool = FunctionTool.from_defaults(fn=lambda location, product_type: get_geospatial_trends(location, product_type), name="get_geospatial_trends")
review_tool = FunctionTool.from_defaults(fn=lambda product_id: analyze_reviews(product_id), name="analyze_reviews")
explanation_tool = FunctionTool.from_defaults(fn=lambda recommendation, user_profile: generate_explanation(recommendation, user_profile), name="generate_explanation")

# Create workers and agents
worker1 = FunctionCallingAgentWorker.from_tools([recommendation_tool, update_profile_tool], llm=OpenAI())
agent1 = worker1.as_agent()

geospatial_worker = FunctionCallingAgentWorker.from_tools([geospatial_tool], llm=OpenAI())
geospatial_agent = geospatial_worker.as_agent()

review_worker = FunctionCallingAgentWorker.from_tools([review_tool], llm=OpenAI())
review_agent = review_worker.as_agent()

explanation_worker = FunctionCallingAgentWorker.from_tools([explanation_tool], llm=OpenAI())
explanation_agent = explanation_worker.as_agent()

# Setup multi-agent framework components
message_queue = SimpleMessageQueue()
control_plane = ControlPlaneServer(
    message_queue=message_queue,
    orchestrator=AgentOrchestrator(llm=OpenAI()),
)

# Create agent services
agent_service = AgentService(
    agent=agent1,
    message_queue=message_queue,
    description="Handles user recommendations and profile updates.",
    service_name="recommendation_agent",
)

geospatial_service = AgentService(
    agent=geospatial_agent,
    message_queue=message_queue,
    description="Handles geospatial trend analysis for recommendations.",
    service_name="geospatial_agent",
)

review_service = AgentService(
    agent=review_agent,
    message_queue=message_queue,
    description="Analyzes product reviews for insights.",
    service_name="review_agent",
)

explanation_service = AgentService(
    agent=explanation_agent,
    message_queue=message_queue,
    description="Generates explanations for recommendations.",
    service_name="explanation_agent",
)

# Ensure that services are launched only once
services = [agent_service, geospatial_service, review_service, explanation_service]

# Launch the system
launcher = LocalLauncher(services, control_plane, message_queue)

# Initial recommendations
try:
    result = launcher.launch_single("Generate product recommendations for the user based on their profile and current trends.")
    logger.info(f"Result: {result}")
except Exception as e:
    logger.error(f"Error generating initial recommendations: {e}")
