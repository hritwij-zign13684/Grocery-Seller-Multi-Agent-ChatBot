from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from langchain_core.output_parsers import StrOutputParser
from langchain_aws import ChatBedrock

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate

from typing import Annotated
from typing_extensions import TypedDict

import boto3 
from Multi_Tools.product_rec_tools import tools
from System_Prompts.system_prompt_1_2 import sys_prompt

model_id = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
bedrock_runtime = boto3.client(service_name="bedrock-runtime")

llm = ChatBedrock(
    model_id= model_id,
    model_kwargs=dict(temperature=0),
    client=bedrock_runtime,
    beta_use_converse_api=True
)

llm_with_tools_1 = llm.bind_tools(tools)    # llm + tools


class State(TypedDict): 
    messages : Annotated[list, add_messages]
   

graphbuilder = StateGraph(State) 

''' 
user_q1 = HumanMessage : Hi
chatbot = AIMessage : hello im antorhopic

user q2 = HumanMessage : xyz ticket book kr 
chatbot : aimessage : tools choise, adesh, input argument : It goes to tool
tools : ToolMessage : ticket has been booked 
chatbot : aimessage : user : You ticket has been book with idlklsd

user q3 : Humanmessage : alkfd

messages_list:

System Prompt

[HumanMessage
AIMessage

HumanMessage
AIMessage

HumanMessage
AIMessage]

HumanMessage : query 2

'''

def chatbot(state : State):
    # print("CORE PRODUCT RE")
    # print(f"state:\n{state}\n\n")

    # system prompt shoulb be at top of the messages list

    message_list = [("system", sys_prompt)] + state['messages']
    response = llm_with_tools_1.invoke(message_list)               # type : AIMessage


    # print("Thinker Node:")
    # print(f"{response = }")
    return {"messages" : [response]}

graphbuilder.add_node("chatbot",chatbot)

from langgraph.prebuilt import ToolNode

tool_node = ToolNode(tools)

graphbuilder.add_node("tools", tool_node)    

def should_continue(state: State):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

graphbuilder.add_conditional_edges("chatbot", should_continue, {'tools': "tools", END : END})

graphbuilder.add_edge("tools", "chatbot")
graphbuilder.add_edge(START, "chatbot")
memory = MemorySaver()
product_recommendation_agent = graphbuilder.compile(checkpointer= memory)