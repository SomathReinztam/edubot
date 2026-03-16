

from sqlalchemy import create_engine, text
from src import settings
from sqlalchemy.orm import sessionmaker
from src import models
from src.apps.DiscordCunkenizer.agentv1.agent import create_chunkenizer
from langchain_core.language_models.chat_models import BaseChatModel


TEMPLATE_1 = """
{idx} -- {date} -- {author_name}:
{content}
"""


engine = create_engine(settings.APP_CONN_STRING)


def get_chumk_text_channel(channel_id : int, limit : int, offset : int):
    Session = sessionmaker(bind=engine)
    session = Session()

    discord_messages_record = session.query(models.DiscordMessage).filter_by(channel_id=channel_id).order_by(models.DiscordMessage.message_create_at).limit(limit=limit).offset(offset=offset).all()

    count = 1
    chunk_text_channel = ""
    for record in discord_messages_record:
        formatted_date = record.message_create_at.strftime("%d/%m/%Y %H:%M")

        msg = TEMPLATE_1.format(idx=count, date=formatted_date, author_name=record.author_name, content=record.content)
        chunk_text_channel += msg
        chunk_text_channel += "\n\n\n"
        count += 1
    
    min_id = discord_messages_record[0].id
    max_id = discord_messages_record[-1].id
    return {"chunk_text_channel" : chunk_text_channel, "min_id":min_id, "max_id":max_id}




# , channel_id : int, min_id : int
def get_chunks_index(llm : BaseChatModel, chunk_text_channel : str):
    chunkenizer_agent = create_chunkenizer(llm=llm)
    initial_state = {"discord_messages":chunk_text_channel}
    agent_response = chunkenizer_agent.invoke(initial_state)
    max_idx = agent_response["max_idx"]
    return max_idx




if __name__=="__main__":
    from langchain_google_genai import ChatGoogleGenerativeAI

    chunk_text_channel = get_chumk_text_channel(channel_id=1357437165738393822, limit=51, offset=0)
    print(chunk_text_channel["chunk_text_channel"])
    print("\n\n")
    print(f"min_id: {chunk_text_channel["min_id"]} \n max_id: {chunk_text_channel["max_id"]}")
    print("\n\n")
    print("\n\n")
    
    
    model = "gemini-2.5-flash"
    llm = ChatGoogleGenerativeAI(model=model, temperature=0.5, google_api_key=settings.GOOGLE_API_KEY)
    text_channel = chunk_text_channel["chunk_text_channel"]

    max_chunk_id = get_chunks_index(llm=llm, chunk_text_channel=text_channel)
    print(f"max_chunk_id: {max_chunk_id} \n\n")
    print(f"chunks scope: {chunk_text_channel['min_id']} -- {chunk_text_channel['max_id'] + max_chunk_id}")




"""
python3 -m src.apps.DiscordCunkenizer.main


"""