from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from enum import Enum
from typing import List, Dict
import pprint
from colorama import Fore, Back, Style

from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool

import pandas as pd

from dotenv import load_dotenv
load_dotenv()

data_path = "/Users/deveshsurve/UNIVERSITY/INFO/7374/Final-Project-SmartCommerce/data_pipeline/data_files/"

customers_df = pd.read_csv(data_path + 'olist_customers_dataset.csv')
orders_df = pd.read_csv(data_path + 'olist_orders_dataset.csv')
order_items_df = pd.read_csv(data_path + 'olist_order_items_dataset.csv')
products_df = pd.read_csv(data_path + 'olist_products_dataset.csv')
product_category_df = pd.read_csv(data_path + 'product_category_name_translation.csv')

class Speaker(str, Enum):
    MAIN_RECOMMENDATION = "main_recommendation"
    USER_ANALYSIS = "user_analysis"
    PRODUCT_ANALYSIS = "product_analysis"
    CONTEXT_AWARE = "context_aware"
    EXPLANATION_GENERATION = "explanation_generation"
    ORCHESTRATOR = "orchestrator"


def get_initial_state() -> Dict:
    return {
        "user_id": None,
        "user_profile": None,
        "recommended_products": [],
        "current_context": None,
        "explanation": None,
        "current_speaker": None,
        "just_finished": False,
    }



def main_recommendation_agent_factory(state: Dict) -> OpenAIAgent:
    def fetch_user_data(user_id: str) -> Dict:
        print("Fetching user data for user:", user_id)
        user_data = customers_df[customers_df['customer_id'] == user_id].to_dict('records')
        if len(user_data) > 0:
            print("User found")
            print(user_data[0])
            return user_data[0]
        else:
            print("User not found")
            return None

    def get_recommended_products(user_profile: Dict) -> List[Dict]:
        """Gets recommended products based on user profile."""
        # Implement recommendation logic here
        print("Getting recommended products")
        return [{"id": "123", "name": "Product A"}, {"id": "456", "name": "Product B"}]

    def store_recommendations(products: List[Dict]) -> None:
        """Stores the recommended products in the state."""
        state["recommended_products"] = products
        print("Storing recommendations")

    def done() -> None:
        """Signals that the main recommendation task is complete."""
        print("Main recommendation is complete")
        state["current_speaker"] = None
        state["just_finished"] = True

    tools = [
        FunctionTool.from_defaults(fn=fetch_user_data),
        FunctionTool.from_defaults(fn=get_recommended_products),
        FunctionTool.from_defaults(fn=store_recommendations),
        FunctionTool.from_defaults(fn=done),
    ]

    system_prompt = f"""
    You are the Main Recommendation Agent responsible for orchestrating the overall recommendation process.
    Your task is to fetch user data, get recommended products, and store them in the state.
    The current user state is:
    {pprint.pformat(state, indent=4)}
    When you have completed the recommendation process, call the "done" tool.
    """

    return OpenAIAgent.from_tools(
        tools,
        llm=OpenAI(model="gpt-4o-mini"),
        system_prompt=system_prompt,
    )


def orchestration_agent_factory(state: Dict) -> OpenAIAgent:
    def check_user_profile() -> bool:
        """Checks if a user profile exists in the state."""
        return state["user_profile"] is not None

    def check_recommendations() -> bool:
        """Checks if recommendations exist in the state."""
        return len(state["recommended_products"]) > 0

    tools = [
        FunctionTool.from_defaults(fn=check_user_profile),
        FunctionTool.from_defaults(fn=check_recommendations),
    ]

    system_prompt = f"""
    You are the Orchestration Agent responsible for deciding which agent to run next.
    The current state of the user is:
    {pprint.pformat(state, indent=4)}

    If a current_speaker is already selected in the state, simply output that value.

    If there is no current_speaker value, look at the chat history and the current state and you MUST return one of these strings identifying an agent to run:
    * "{Speaker.MAIN_RECOMMENDATION.value}" - if the user needs initial recommendations
    * "{Speaker.USER_ANALYSIS.value}" - if user profile analysis is needed
    * "{Speaker.PRODUCT_ANALYSIS.value}" - if product analysis is needed
    * "{Speaker.CONTEXT_AWARE.value}" - if contextual information needs to be incorporated
    * "{Speaker.EXPLANATION_GENERATION.value}" - if explanations for recommendations are needed

    Output one of these strings and ONLY these strings, without quotes.
    NEVER respond with anything other than one of the above five strings. DO NOT be helpful or conversational.
    """

    return OpenAIAgent.from_tools(
        tools,
        llm=OpenAI(model="gpt-4o-mini", temperature=0.4),
        system_prompt=system_prompt,
    )

def user_analysis_agent_factory(state: Dict) -> OpenAIAgent:
    def analyze_user_profile(user_profile: Dict) -> Dict:
        """Analyzes the user profile and returns insights."""
        # Implement user analysis logic here
        print("Analyzing user profile")
        return {"   name": "John Doe", "location": "New York"}
    
    def store_user_profile_analysis(analysis: Dict) -> None:
        """Stores the user profile analysis in the state."""
        state["user_profile"] = analysis
        print("Storing user profile analysis")

    def done() -> None:
        """Signals that the user analysis task is complete."""
        print("User analysis is complete")
        state["current_speaker"] = None
        state["just_finished"] = True

    tools = [
        FunctionTool.from_defaults(fn=analyze_user_profile),
        FunctionTool.from_defaults(fn=store_user_profile_analysis),
        FunctionTool.from_defaults(fn=done),
    ]

    system_prompt = f"""
    You are the User Analysis Agent responsible for analyzing the user profile.
    Your task is to analyze the user profile and store the analysis in the state.
    The current user state is:
    {pprint.pformat(state, indent=4)}
    When you have completed the analysis, call the "done" tool.
    """

    return OpenAIAgent.from_tools(
        tools,
        llm=OpenAI(model="gpt-4o-mini"),
        system_prompt=system_prompt,
    )

def product_analysis_agent_factory(state: Dict) -> OpenAIAgent:
    def analyze_product(product_id: str) -> Dict:
        """Analyzes the product and returns insights."""
        # Implement product analysis logic here
        print(f"Analyzing product {product_id}")
        return {"id": product_id, "name": "Product A", "price": 100}

    def store_product_analysis(analysis: Dict) -> None:
        """Stores the product analysis in the state."""
        state["current_context"] = analysis
        print("Storing product analysis")

    def done() -> None:
        """Signals that the product analysis task is complete."""
        print("Product analysis is complete")
        state["current_speaker"] = None
        state["just_finished"] = True

    tools = [
        FunctionTool.from_defaults(fn=analyze_product),
        FunctionTool.from_defaults(fn=store_product_analysis),
        FunctionTool.from_defaults(fn=done),
    ]

    system_prompt = f"""
    You are the Product Analysis Agent responsible for analyzing the product.
    Your task is to analyze the product and store the analysis in the state.
    The current user state is:
    {pprint.pformat(state, indent=4)}
    When you have completed the analysis, call the "done" tool.
    """

    return OpenAIAgent.from_tools(
        tools,
        llm=OpenAI(model="gpt-4o-mini"),
        system_prompt=system_prompt,
    )

def context_aware_agent_factory(state: Dict) -> OpenAIAgent:
    def incorporate_context(context: Dict) -> None:
        """Incorporates context into the recommendations."""
        # Implement context incorporation logic here
        print("Incorporating context")

    def done() -> None:
        """Signals that the context incorporation task is complete."""
        print("Context incorporation is complete")
        state["current_speaker"] = None
        state["just_finished"] = True

    tools = [
        FunctionTool.from_defaults(fn=incorporate_context),
        FunctionTool.from_defaults(fn=done),
    ]

    system_prompt = f"""
    You are the Context-Aware Agent responsible for incorporating context into the recommendations.
    Your task is to incorporate context into the recommendations based on the current context.
    The current user state is:
    {pprint.pformat(state, indent=4)}
    When you have completed the context incorporation, call the "done" tool.
    """

    return OpenAIAgent.from_tools(
        tools,
        llm=OpenAI(model="gpt-4o-mini"),
        system_prompt=system_prompt,
    )

def explanation_generation_agent_factory(state: Dict) -> OpenAIAgent:
    def generate_explanation(recommended_products: List[Dict]) -> str:
        """Generates an explanation for the recommended products."""
        # Implement explanation generation logic here
        print("Generating explanation")
        return "Based on your profile, we recommend Product A and Product B."

    def store_explanation(explanation: str) -> None:
        """Stores the explanation in the state."""
        state["explanation"] = explanation
        print("Storing explanation")

    def done() -> None:
        """Signals that the explanation generation task is complete."""
        print("Explanation generation is complete")
        state["current_speaker"] = None
        state["just_finished"] = True

    tools = [
        FunctionTool.from_defaults(fn=generate_explanation),
        FunctionTool.from_defaults(fn=store_explanation),
        FunctionTool.from_defaults(fn=done),
    ]

    system_prompt = f"""
    You are the Explanation Generation Agent responsible for generating explanations for the recommendations.
    Your task is to generate an explanation for the recommended products and store it in the state.
    The current user state is:
    {pprint.pformat(state, indent=4)}
    When you have completed the explanation generation, call the "done" tool.
    """

    return OpenAIAgent.from_tools(
        tools,
        llm=OpenAI(model="gpt-4o-mini"),
        system_prompt=system_prompt,
    )

def run() -> None:
    state = get_initial_state()
    root_memory = ChatMemoryBuffer.from_defaults(token_limit=8000)

    while True:
        user_msg_str = input("> ").strip()
        current_history = root_memory.get()

        if state["current_speaker"]:
            next_speaker = state["current_speaker"]
        else:
            orchestration_response = orchestration_agent_factory(state).chat(user_msg_str, chat_history=current_history)
            next_speaker = str(orchestration_response).strip()

        if next_speaker == Speaker.MAIN_RECOMMENDATION:
            current_speaker = main_recommendation_agent_factory(state)
        elif next_speaker == Speaker.USER_ANALYSIS:
            current_speaker = user_analysis_agent_factory(state)
        elif next_speaker == Speaker.PRODUCT_ANALYSIS:
            current_speaker = product_analysis_agent_factory(state)
        elif next_speaker == Speaker.CONTEXT_AWARE:
            current_speaker = context_aware_agent_factory(state)
        elif next_speaker == Speaker.EXPLANATION_GENERATION:
            current_speaker = explanation_generation_agent_factory(state)
        else:
            print("Invalid speaker selected")
            continue

        state["current_speaker"] = next_speaker

        response = current_speaker.chat(user_msg_str, chat_history=current_history)
        print(Fore.MAGENTA + str(response) + Style.RESET_ALL)

        new_history = current_speaker.memory.get_all()
        root_memory.set(new_history)

if __name__ == "__main__":
    run()

# Customer ID: 9ef432eb6251297304e76186b10a928d