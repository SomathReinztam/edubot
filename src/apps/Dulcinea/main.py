from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from src.apps.Dulcinea.graphs.create_dulcineav1 import create_dulcinea
from src import settings
from typing import Literal

from sqlalchemy import create_engine
import json


def get_dulci_report(query : str, guild_name : Literal["Unergy", "The_Sun_Factory"], channel_name : str):

    guild_dict = {"Unergy":772855809406271508, "The_Sun_Factory":1308885706621452369}
    guild_id = guild_dict[guild_name]

    if guild_name == "Unergy":
        path_unergy = settings.ROOT / "data" / "Unergy.json"
        with open(path_unergy, 'r') as f:
            channels_unergy_dict = json.load(f)
        channel_id = channels_unergy_dict.get(channel_name, None)   
    else:
        path_unergy = settings.ROOT / "data" / "TheSunFactory.json"
        with open(path_unergy, 'r') as f:
            channels_unergy_dict = json.load(f)
        channel_id = channels_unergy_dict.get(channel_name, None)
    
    

    model = "gemini-2.0-flash"
    llm = ChatGoogleGenerativeAI(model=model, temperature=0.5, google_api_key=settings.GOOGLE_API_KEY)

    path = settings.ROOT / "_docs" / "dulcineadb" / "proyectobot.db"
    engine = create_engine(f"sqlite:///{path}")

    dulcinea = create_dulcinea(llm=llm, engine=engine)
    initial_state = {"guild_id":guild_id, "channel_id":channel_id, "query":query}
    agent_response = dulcinea.invoke(initial_state)

    report = agent_response["result"]

    return report
    





