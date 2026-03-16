

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, BigInteger, String, DateTime, Text, func, JSON


class Base(DeclarativeBase):
    pass


# class DiscordMessage(Base):
#     __tablename__ = "discord_messages"

#     id = Column(BigInteger, primary_key=True, autoincrement=True)

#     discord_message_id = Column(BigInteger, unique=True, index=True)

#     guild_id = Column(BigInteger, index=True)
#     guild_name = Column(String)

#     channel_id = Column(BigInteger, index=True)
#     channel_name = Column(String)

#     author_id = Column(BigInteger, index=True)
#     author_name = Column(String)

#     content = Column(Text, nullable=True)

#     reply_to = Column(BigInteger)

#     attachments = Column(JSON)

#     message_create_at = Column(DateTime, index=True)
#     edited_at = Column(DateTime)

#     inserted_at = Column(DateTime, server_default=func.now())





class DiscordGuild(Base):
    __tablename__="discord_servers"

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    create_at = Column(DateTime, index=True) # fecha de creacion del server
    inserted_at = Column(DateTime, server_default=func.now())



class DiscordUser(Base):
    __tablename__="discord_users"

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    guild_id = Column(BigInteger)
    joined_at = Column(DateTime, index=True) # fecha en la que se unio al server
    inserted_at = Column(DateTime, server_default=func.now())



class DiscordChannel(Base):
    __tablename__="discord_channels"

    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger)
    name = Column(String)
    parent_channel_id = Column(BigInteger) # Si es un hilo, cual es el canal del hilo
    create_at = Column(DateTime, index=True)
    last_messages_at = Column(DateTime, index=True) # Fecha del ultimo mensaje
    inserted_at = Column(DateTime, server_default=func.now())



class DiscordMessage(Base):
    __tablename__ = "discord_messages"

    id = Column(BigInteger, unique=True, index=True, primary_key=True)
    guild_id = Column(BigInteger, index=True)
    channel_id = Column(BigInteger, index=True)
    author_id = Column(BigInteger, index=True)
    content = Column(Text, nullable=True)
    reply_to = Column(BigInteger)
    attachments = Column(JSON)
    message_create_at = Column(DateTime, index=True)
    inserted_at = Column(DateTime, server_default=func.now())



