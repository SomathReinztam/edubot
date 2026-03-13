from typing import TypedDict
from sqlalchemy.engine import Engine
from ..utils.db_utils import retrive_sqlite_messages
from ..prompts.dulcinea import PROMPT_1

from langchain_core.language_models.chat_models import BaseChatModel

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

def create_dulcinea(llm : BaseChatModel, engine : Engine) -> CompiledStateGraph:

    class State(TypedDict):
        # initial state
        guild_id : int
        channel_id : int
        query : str

        messages : str
        result : str

    
    def retrive_messages_node(state : State) -> State:
        guild_id = state['guild_id']
        channel_id = state['channel_id']

        messages = retrive_sqlite_messages(engine=engine, guild_id=guild_id, channel_id=channel_id)

        return {"messages":messages}
    

    def generate_response(state : State) -> State:
        messages = state['messages']
        query = state['query']

        prompt = PROMPT_1.format(messages=messages, query=query)
        ai_response = llm.invoke(prompt)

        return {"result":ai_response.content}
    
    builder = StateGraph(State)

    builder.add_node("retrive_messages_node", retrive_messages_node)
    builder.add_node("generate_response", generate_response)

    builder.add_edge(START, "retrive_messages_node")
    builder.add_edge("retrive_messages_node", "generate_response")
    builder.add_edge("generate_response", END)

    return builder.compile()
    


        
