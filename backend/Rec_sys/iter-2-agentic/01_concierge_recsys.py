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
root_memory = ChatMemoryBuffer.from_defaults(token_limit=8000)



"""
Things to know when designing a concierge type system:

1. You need an initail state for the system
2. You need to define the speakers ( i.e the agents that will be responsible for different tasks)
3. You need to define the agents that will be responsible for the different tasks
4. You need to define the tools that the agents will use to complete their tasks
5. You need to define the system prompt that will be used to guide the agents
6. You need to define the orchestration agent that will decide which agent to call next
7. You need to define the run function that will run the system

"""

class Speaker(str, Enum):
    USER_ANALYSIS = "user_analysis"
    CONCIERGE = "concierge"
    ORCHESTRATOR = "orchestrator"

def get_initial_state() -> Dict:
    return {
        "user_details": None,
        "current_speaker": None,
        "just_finished": False,
    }

def concierge_agent_factory(state: dict) -> OpenAIAgent:

    def dummy_tool() -> bool:
        """A tool that does nothing."""
        print("Doing nothing.")

    tools = [
        FunctionTool.from_defaults(fn=dummy_tool)
    ]

    system_prompt = (f"""
        You are a helpful assistant that is helping a user navigate a recommendation system.
        Your job is to ask the user questions to figure out what they want to do, and give them the available things they can do.
        If you already have user info 
        * ask the user if are simply browsing and would be interested in recommendations
        * are looking for something specific. 

        The current state of the user is:
        {pprint.pformat(state, indent=4)}
    """)

    return OpenAIAgent.from_tools(
        tools,
        llm=OpenAI(model="gpt-4o-mini"),
        system_prompt=system_prompt,
    )


def orchestration_agent_factory(state: dict) -> OpenAIAgent:

    def has_balance() -> bool:
        """Useful for checking if an account has a balance."""
        print("Orchestrator checking if account has a balance")
        return (state["account_balance"] is not None)
    
    def is_authenticated() -> bool:
        """Checks if the user has a session token."""
        print("Orchestrator is checking if authenticated")
        return (state["session_token"] is not None)

    tools = [
        FunctionTool.from_defaults(fn=has_balance),
        FunctionTool.from_defaults(fn=is_authenticated),
    ]
    
    system_prompt = (f"""
        You are on orchestration agent.
        Your job is to decide which agent to run based on the current state of the user and what they've asked to do. Agents are identified by short strings.
        What you do is return the name of the agent to run next. You do not do anything else.
        
        The current state of the user is:
        {pprint.pformat(state, indent=4)}

        If a current_speaker is already selected in the state, simply output that value.

        If there is no current_speaker value, look at the chat history and the current state and you MUST return one of these strings identifying an agent to run:
        * "{Speaker.USER_ANALYSIS.value}" - Choose this FIRST if you the user information is empty. 
        * "{Speaker.CONCIERGE.value}" - if the user wants to do something else, or hasn't said what they want to do, or you can't figure out what they want to do. Choose this by default.

        Output one of these strings and ONLY these strings, without quotes.
        NEVER respond with anything other than one of the above five strings. DO NOT be helpful or conversational.
    """)

    return OpenAIAgent.from_tools(
        tools,
        llm=OpenAI(model="gpt-4o-mini",temperature=0.4),
        system_prompt=system_prompt,
    )

def user_analysis_agent_factory(state: Dict) -> OpenAIAgent:
    def fetch_user_info() -> str:
        """Gets the user intent from the state."""
        state["user_info"] = "{'user_details':'Likes Ipad'}"
        return state["user_info"]

    def done() -> None:
        """Signals that the main recommendation task is complete."""
        print("User Analysis is complete. State updated")
        state["current_speaker"] = orchestration_agent_factory(state).chat("User Analysis is complete. State updated", chat_history=current_history)
        state["just_finished"] = True

    tools = [
        FunctionTool.from_defaults(fn=fetch_user_info),
        FunctionTool.from_defaults(fn=done),
    ]

    system_prompt = f"""
    You are the User Analysis Agent. Your job is fetch information about the user so we can suggest them better recommendations.
    The current user state is:
    {pprint.pformat(state, indent=4)}
    When you have completed state update process, call the "done" tool.
    """

    return OpenAIAgent.from_tools(
        tools,
        llm=OpenAI(model="gpt-4o-mini"),
        system_prompt=system_prompt,
    )

def run() -> None:
    state = get_initial_state()

    while True:
        user_msg_str = input("> ").strip()
        current_history = root_memory.get()

        if state["current_speaker"]:
            next_speaker = state["current_speaker"]
        else:
            orchestration_response = orchestration_agent_factory(state).chat(user_msg_str, chat_history=current_history)
            next_speaker = str(orchestration_response).strip()

        if next_speaker == Speaker.USER_ANALYSIS:
            print("User analysis agent is selected")
            current_speaker = user_analysis_agent_factory(state)
        elif next_speaker == Speaker.CONCIERGE:
            print("Concierge agent selected")
            current_speaker = concierge_agent_factory(state)
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