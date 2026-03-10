import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

root = Path(__file__).resolve().parent.parent
path = root / "_docs" / "dulcineadb" / "proyectobot.db"

engine = create_engine(f"sqlite:///{path}")



TEMPLATE_1 = """

El mensaje tiene autor: {author_name}, con fecha {created_at}, y contenido:

{content}

---
"""


TEMPLATE_2 = """

El mensaje tiene autor: {author_name} con fecha {created_at} y contenido:

{content}

Y el mensaje responde al usuario {author_name_response} con fecha {created_at_response} y contenido

{content_response}

---
"""



TEMPLATE_3 = """

{author_name} - {created_at}:

{content}

---
"""



QUERY = """
SELECT
    id,
    channel_name,
    author_name,
    content,
    reply_to_msg_id,
    created_at
FROM discord_messages
WHERE channel_id = '1441518428333543506'
ORDER BY created_at DESC
LIMIT 3;
"""

df = pd.read_sql(QUERY, engine)
df['created_at'] = pd.to_datetime(df["created_at"])
df['created_at'] = df['created_at'].dt.strftime("%d %B %Y - %H:%M")

for i in range(df.shape[0]):
    msg = TEMPLATE_3.format(
        author_name=df.loc[i, 'author_name'],
        created_at=df.loc[i, 'created_at'],
        content=df.loc[i, 'content']
    )
    print(msg)
    print("\n"*5)

"""
python3 -m datos.getdata1

"""