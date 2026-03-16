from typing import TypedDict

from src.apps.DiscordCunkenizer.agentv1.prompts import CHUNKING_PROMPT_3

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import JsonOutputParser

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph




def create_chunkenizer(llm : BaseChatModel) -> CompiledStateGraph:

    parser = JsonOutputParser()
    
    class State(TypedDict):
        # initial state
        discord_messages : str

        max_idx : int | bool

    def get_max_index_node(state : State) -> State:
        discord_messages = state["discord_messages"]

        prompt = CHUNKING_PROMPT_3.format(discord_messages=discord_messages)
        ai_message = llm.invoke(prompt)
        print(ai_message.usage_metadata)
        json_message = parser.parse(ai_message.content)

        max_idx = json_message["max_idx"]

        return {"max_idx":max_idx}
    
    builder = StateGraph(State)

    builder.add_node("get_max_index_node", get_max_index_node)

    builder.add_edge(START, "get_max_index_node")
    builder.add_edge("get_max_index_node", END)

    return builder.compile()
    


