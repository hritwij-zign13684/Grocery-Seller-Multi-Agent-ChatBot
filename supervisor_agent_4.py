from Seperate_Agents.product_rec_agent import product_recommendation_agent as agent_1
from Seperate_Agents.order_processing_agent import order_processing_agent as agent_2
from Seperate_Agents.support_agent import support_agent as agent_3

from typing import Literal
from typing_extensions import TypedDict, Annotated
import boto3 

from typing import Optional
from pydantic import BaseModel, Field, constr
import json

from typing import Annotated
from langchain_aws import ChatBedrock
from langgraph.types import Command 
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

# from System_Prompts.supervisor_sys_prompt_for_next import sys_prompt as s1
# from System_Prompts.supervisor_sys_prompt_for_message_2 import sys_prompt as s2
from System_Prompts.super_agent_sys_prompt_2 import sys_prompt as s3

from typing import Annotated
from langgraph.prebuilt import InjectedState, create_react_agent

model_id = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
bedrock_runtime = boto3.client(service_name="bedrock-runtime")

llm = ChatBedrock(
    model_id= model_id,
    model_kwargs=dict(temperature=0),
    client=bedrock_runtime,
    beta_use_converse_api=True
)

# class State(TypedDict):
#     messages : Annotated[list, add_messages]
#     next : Annotated[list, add_messages] 


# # this is the agent function that will be called as tool
# # notice that you can pass the state to the tool via InjectedState annotation
# def agent_1(state: Annotated[dict, InjectedState]):
#     # you can pass relevant parts of the state to the LLM (e.g., state["messages"])
#     # and add any additional logic (different models, custom prompts, structured output, etc.)
#     response = model.invoke(...)
#     # return the LLM response as a string (expected tool response format)
#     # this will be automatically turned to ToolMessage
#     # by the prebuilt create_react_agent (supervisor)
#     return response.content

# def agent_2(state: Annotated[dict, InjectedState]):
#     response = model.invoke(...)
#     return response.content

@tool(name_or_callable ='product_recommendation_agent', description="Product Recommendation Agent for exploring and retrieving product information")
def product_recommendation_agent(state: Annotated[dict, InjectedState]) -> str:
    """
    This module provides a set of capabilities for exploring and retrieving product information from a grocery dataset.

    Capabilities:
    1. explore_options:
    - Functionality: Shows random products from the provided list of sub-categories.
    - Parameters:
        - check_sub_cat_list (list): List of sub-categories to filter products.
        - request (str): A request explaining the user's need to Product Recommendation Agent tool
    - Returns: A JSON string containing details of randomly selected products from the specified sub-categories.

    2. explore_options_with_price:
    - Functionality: Explores product options within specified price ranges or retrieves top/bottom priced products in given sub-categories.
    - Parameters:
        - check_sub_cat_list (list): List of sub-categories to filter products.
        - price_lower_limit (float, optional): Lower limit of the price range. Defaults to False.
        - price_upper_limit (float, optional): Upper limit of the price range. Defaults to False.
        - asked_max (bool, optional): If True, returns top 3 most expensive products in each sub-category. Defaults to False.
        - asked_min (bool, optional): If True, returns top 3 least expensive products in each sub-category. Defaults to False.
        - request (str): A request explaining the user's need to Product Recommendation Agent tool
    - Returns: A JSON string containing products that match the specified criteria.

    3. retrieve_with_prd_id:
    - Functionality: Retrieves product information based on a list of product IDs.
    - Parameters:
        - check_prod_id_list (list of integers): List of product IDs to filter products.
        - request (str): A request explaining the user's need to Product Recommendation Agent tool
    - Returns: A JSON string containing details of products that match the specified product IDs.

    4. retrieve_with_pincode:
    - Functionality: Retrieves product information based on the pincode of the nearest seller.
    - Parameters:
        - nearest_seller_pincode (int): Pincode of the seller.
        - request (str): A request explaining the user's need to Product Recommendation Agent tool
    - Returns: A JSON string containing details of products sold by the seller with the specified pincode.

    """


    print("PRODUCT RECOMMENDATION NODE:")
    # print(f"Length of state messages: {len(state['messages'])}")
    print(f"state: \n{state}\n\n")
    
    supervisor_conveted_msg = HumanMessage(content= str(state["messages"][-1].tool_calls[0]['args']), name="SUPERVISOR",id = state["messages"][-1].id)
    # state["messages"].append(supervisor_conveted_msg)
    print(f"Supervisor Message: {supervisor_conveted_msg.content}"); print()
    # response = agent_1.invoke({"messages": [supervisor_conveted_msg]})
    response = agent_1.invoke({"messages": state['messages']+[supervisor_conveted_msg]})
    # print(f"{response["messages"][-1] = }")
    # print()
    # print(f"response = {response}"); print()
    # response_converted_msg = ToolMessage(
    #                 content=response['messages'][-1].content,
    #                 name=response["name"],
    #                 tool_call_id=state["messages"][-1].content[1]['id'],
                # )
    # print(f"Agents response: {response['messages'][-1].content}"); print()
    return response['messages'][-1].content

@tool(name_or_callable="order_processing_agent", description="Order Processing Agent for calculating delivery details and saving order data")
def order_processing_agent(state: Annotated[dict, InjectedState]) :
    """
    This module provides a set of capabilities for processing orders, calculating delivery details, and saving order data.

    Capabilities:
    1. calculate_distance:
    - Functionality: Calculates the geographical distance between two pincodes.
    - Parameters:
        - pincode1 (int): Pincode of location 1.
        - pincode2 (int): Pincode of location 2.
    - Returns: A float representing the distance in kilometers.

    2. calculate_delivery_charge:
    - Functionality: Calculates the delivery charge based on distance and delivery speed preference.
    - Parameters:
        - distance_km (float): The distance in kilometers for delivery.
        - delivery_speed (str): The user's preferred delivery speed. Options: ["standard", "express", "same_day", "instant"].
        - request (str): A   request explaining the user's need to Order Processing Assistant.

    - Returns: A float representing the total delivery charge in INR.

    3. calculate_delivery_time:
    - Functionality: Calculates the estimated delivery date and time based on delivery speed.
    - Parameters:
        - delivery_speed (str): The user's preferred delivery speed. Options: ["standard", "express", "same_day", "instant"].
        - request (str): A   request explaining the user's need to Order Processing Assistant.
    - Returns: A datetime object representing the estimated delivery date and time.

    4. calculate_total_price:
    - Functionality: Calculates the total price of products based on their IDs, quantities, and delivery charges.
    - Parameters:
        - check_prod_id_list (list): List of product IDs to filter products.
        - prod_quantity_list (list): List of quantities corresponding to each product ID.
        - total_delivery_charges (float): Total delivery charges for all products.
        - request (str): A   request explaining the user's need to Order Processing Assistant.
    - Returns: A float representing the total price of the specified products.

    5. generate_order_id:
    - Functionality: Generates a unique order ID for placing an order.
    - Parameters: None.
    - Returns: A string representing the unique order ID.

    6. save_delivery_data:
    - Functionality: Saves delivery details into a CSV file.
    - Parameters:
        - order_id (str): Unique order ID.
        - user_id (int): User ID who placed the order.
        - product_id (list[int]): List of IDs of the purchased products.
        - quantity (list[int]): List of quantities of the items.
        - product_name (list[str]): List of names of the products.
        - order_date (str): Order placement date and time (YYYY-MM-DD HH:MM).
        - delivery_speed (str): Delivery preference (standard, express, etc.).
        - distance_km (float): Distance in kilometers.
        - delivery_charge (float): Calculated delivery charge.
        - estimated_delivery_date (str): Expected delivery date (YYYY-MM-DD HH:MM).
        - seller_pincode (int): Seller’s pincode.
        - buyer_pincode (int): Buyer’s pincode.
        - delivery_status (str): Current delivery status.
        - total_order_value (float): Total order cost.
        - remarks (str): Additional instructions.
        - filename (str): CSV file to save data. Defaults to "delivery_details.csv".
        - request (str): A   request explaining the user's need to Order Processing Assistant.
    - Returns: A string confirming successful saving of the order data.

    All tools are designed to streamline order processing and delivery management, ensuring accurate calculations and data storage.
    """
    print("ORDER PROCESSING NODE:")
    print(f"state: \n{state}\n\n")
    supervisor_conveted_msg = HumanMessage(content= str(state["messages"][-1].tool_calls[0]['args']), name="SUPERVISOR",id = state["messages"][-1].id)
    print(f"Supervisor Message: {supervisor_conveted_msg.content}"); print()
    # state["messages"].append(supervisor_conveted_msg)
    response = agent_2.invoke({"messages": state['messages']+[supervisor_conveted_msg]})
    # print(f"{response["messages"][-1] = }")
    # print()
    # print(f"response = {response}"); print()
    # print(f"Agents response: {response['messages'][-1].content}"); print()
    return response['messages'][-1].content


@tool(name_or_callable="support_agent", description="Support Agent for existing orders and web based queries")
def support_agent(state: Annotated[dict, InjectedState]) :
    """
    This module provides a set of tools for managing and supporting order-related operations.

    Tools:
    1. get_order_details:
    - Functionality: Retrieves order details from a CSV file based on the provided order ID.
    - Parameters:
        - order_id (str): The order ID to search for.
        - request (str): A   request explaining the user's need to Support Agent Assistant.
    - Returns: A JSON-formatted string containing all rows with the specified order ID.

    2. modify_order_quantities:
    - Functionality: Modifies the quantity of specific products in an existing order and updates the total order value.
    - Parameters:
        - order_id (str): ID of the order to modify.
        - product_ids (list): List of product IDs to update.
        - quantities (list): List of corresponding new quantities.
        - request (str): A   request explaining the user's need to Support Agent Assistant.
    - Returns: A string indicating success or an error message.

    3. cancel_order:
    - Functionality: Cancels an order by setting the delivery status to "Canceled" in the CSV file.
    - Parameters:
        - order_id (str): The ID of the order to cancel.
        - request (str): A   request explaining the user's need to Support Agent assistant Assistant.
    - Returns: A string indicating success or an error message.

    4. tavily_tool:
    - Functionality: Provides search results using the TavilySearchResults tool.
    - Parameters:  (configured with a maximum of 5 results).
        - request (str): A   request explaining the user's need to Support Agent Assistant.
    - Returns: Search results based on the Tavily API.

    All tools are designed to streamline order management, including retrieval, modification, and cancellation of orders, as well as integration with Tavily search functionality.
    """

    print("SUPPORT AGENT:")
    # print(f"state: \n{state = }\n\n")

    supervisor_conveted_msg = HumanMessage(content= str(state["messages"][-1].tool_calls[0]['args']), name="SUPERVISOR",id = state["messages"][-1].id)
    
    # state["messages"].append(supervisor_conveted_msg)
    print(f"Supervisor Message: {supervisor_conveted_msg.content}"); print()
    
    response = agent_3.invoke({"messages": state['messages'] + [supervisor_conveted_msg]})
    
    # print(f"{response["messages"][-1] = }")
    # print()
    # print(f"response = {response}"); print()

    # print(f"Agents response: {response['messages'][-1].content}"); print()
    return response['messages'][-1].content

# builder = StateGraph(State)
# builder.add_node(goto_decider)
# builder.add_node(supervisor_message)
# builder.add_node(product_recommendation_agent_node)
# builder.add_node(order_processing_agent_node)
# builder.add_node(support_agent_node)

# builder.add_edge(START, "goto_decider")
# memory = MemorySaver()
# multi_graph = builder.compile(checkpointer= memory)

tools = [product_recommendation_agent, order_processing_agent, support_agent]

# the simplest way to build a supervisor w/ tool-calling is to use prebuilt ReAct agent graph
# that consists of a tool-calling LLM node (i.e. supervisor) and a tool-executing node

memory = MemorySaver()

supervisor_agent = create_react_agent(llm, tools,prompt= s3 ,checkpointer=memory,name="supervisor_agent")

"""
normal case:
user - chatbot - user
human : aimessage

user - chatbot - tool - chatbot - user
human - aimesaage - toolmessage - aimessage

multi agent case:
user - supervisor - tool: agent_1 - supervisor - user
human - aimessage - input: aimessage 
if aimessage is calling an agent it wont accept it and throw error
therefore conver to humanmessage

humanmessage


tavily is not llm, agent, ai
tavily is a tool : input : aimessage


tool is ai


api : input: marks: int

@tool
def hp_api(marks:int):
    <<logic>>
    if <<logic>> is a api : input marks: int

    if <<logic>> is graph or ai or agent : input: humanmessage
    
    return log


"""