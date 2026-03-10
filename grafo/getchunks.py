from pandas import DataFrame
from .prompts import TEMPLATE_3
from pathlib import Path

root = Path(__file__).resolve().parent.parent
path = root / "_docs" / "graphdata"

path.mkdir(parents=True, exist_ok=True)


# Esto se puede hacer async
def get_chunk_convertations_from_chanel(df : DataFrame, inf : int, sub : int, idx : int):
    """
    Asumo que el el df hay una columna con nombre del autor, contenido del mensaje, y fecha
    """
    doc = ""
    for i in range(inf, sub):
        msg = TEMPLATE_3.format(
            author_name=df.loc[i, 'author_name'],
            created_at=df.loc[i, 'created_at'],
            content=df.loc[i, 'content']
        )
        doc += msg
        doc += "\n\n"

    path_doc = path / f"discord_chanel_{idx}.txt"
    with open(path_doc, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"chunk {idx} guardado exitosamente")



if __name__=="__main__":
    from sqlalchemy import create_engine, text
    import pandas as pd

    db_path = root / "_docs" / "dulcineadb" / "proyectobot.db"
    engine = create_engine(f"sqlite:///{db_path}")


    QUERY = text("""
    SELECT
        id,
        channel_name,
        author_name,
        content,
        reply_to_msg_id,
        created_at
    FROM discord_messages
    WHERE channel_id = '1441518428333543506'
    """)

    df = pd.read_sql(QUERY, engine)
    df['created_at'] = pd.to_datetime(df["created_at"])
    df['created_at'] = df['created_at'].dt.strftime("%d %B %Y - %H:%M")

    #print(df)

    n = 0
    x = 0
    y = 50
    N = df.shape[0]
    while (y < N) and (x<N):
        df_piece = df.iloc[x:y, :]
        get_chunk_convertations_from_chanel(df=df_piece, inf=x, sub=y, idx=n)
        n += 1
        x += 50
        y += 50
    print(f"\n {x}, {y} \n")
    if x < N:
        df_piece = df.iloc[x:, :]
        get_chunk_convertations_from_chanel(df=df_piece, inf=x, sub=N, idx=n)





"""
python3 -m neo4j.getchunks

"""
    