from sqlalchemy.engine import Engine
from ..prompts.templates import SQLITE_QUERY_1, MESSAGE_TEMPLATE
import pandas as pd


def retrive_sqlite_messages(engine : Engine, guild_id : int, channel_id : int):
    df = pd.read_sql(SQLITE_QUERY_1, engine, params={"guild_id": guild_id, "channel_id":channel_id})
    df['created_at'] = pd.to_datetime(df["created_at"])
    df['created_at'] = df['created_at'].dt.strftime("%d %B %Y - %H:%M")

    doc = ""
    for i in range(df.shape[0]):
        doc += MESSAGE_TEMPLATE.format(
            date=df.loc[i, "created_at"],
            author_name=df.loc[i, "author_name"],
            content=df.loc[i, "content"]
        )
        doc += "\n\n"

    return doc


if __name__=="__main__":
    from src.settings import ROOT
    from sqlalchemy import create_engine

    path = ROOT / "_docs" / "dulcineadb" / "proyectobot.db"
    engine = create_engine(f"sqlite:///{path}")

    doc = retrive_sqlite_messages(engine=engine, guild_id=1308885706621452369, channel_id=1414989101882413197)
    print(doc)


    


"""
python3 -m src.apps.Dulcinea.utils.db_utils

"""