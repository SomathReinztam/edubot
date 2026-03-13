from sqlalchemy import text

SQLITE_QUERY_1 = text("""
select 
    author_name,
    content,
    created_at
from discord_messages
where 
    guild_id = :guild_id and
    channel_id = :channel_id
order by created_at;
""")


# from sqlalchemy import text

# query = text("""
# select 
#     content,
#     created_at
# from discord_messages
# where 
#     guild_id = :guild_id
# order by created_at;
# """)

# df = pd.read_sql(query, engine, params={"guild_id": 1})




MESSAGE_TEMPLATE = """
{date} -- {author_name}: 
{content}. 
"""
