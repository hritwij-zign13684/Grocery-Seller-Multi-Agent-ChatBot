from langchain_aws import ChatBedrock

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END

from typing import Annotated
from typing_extensions import TypedDict
from typing import Optional
from pydantic import BaseModel, Field
import boto3 

model_id = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
bedrock_runtime = boto3.client(service_name="bedrock-runtime")
llm = ChatBedrock(
    model_id= model_id,
    model_kwargs=dict(temperature=0),
    client=bedrock_runtime,
    beta_use_converse_api=True
)


class State(TypedDict):
    messages : Annotated[list, add_messages]

# Pydantic
class Joke(BaseModel):
    """Joke to tell user."""

    setup: str = Field(description="The setup of the joke")
    punchline: str = Field(description="The punchline to the joke")
    rating: Optional[int] = Field(
        default=None, description="How funny the joke is, from 1 to 10"
    )

structured_llm = llm.with_structured_output(Joke)

def chatbot(state : State):
    response = structured_llm.invoke(state['messages'])
    return {"messages" : [response]}

graphbuilder = StateGraph(State) 
graphbuilder.add_node("chatbot",chatbot)

graphbuilder.add_edge(START, "chatbot")
graphbuilder.add_edge("chatbot", END)
memory = MemorySaver()
structured_graph = graphbuilder.compile(checkpointer= memory)