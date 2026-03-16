import discord
from typing import Optional
from src import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src import models


class DiscordEchoSaverBot(discord.Client):
    def __init__(
        self,
        *,
        intents: discord.Intents,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ):
        super().__init__(intents=intents)
        self.engine = create_engine(settings.APP_CONN_STRING)
        self.guild_id = guild_id
        self.channel_id = channel_id

    async def on_ready(self):
        print(f"🤖 Conectado como {self.user}")
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # await self.save_guild_data(session)
        await self.save_user_data(session)
        # await self.save_channel_data(session)

        # if self.guild_id and self.channel_id:
        #     await self.get_discord_channel_history(
        #         session, self.guild_id, self.channel_id
        #     )

        session.close()  # Close session when done

        await self.close()  # Close bot after operations




    async def save_guild_data(self, session):
        print("\n📦 Guardando información de servidores:")
        for guild in self.guilds:
            existing_guild = (
                session.query(models.DiscordGuild).filter_by(id=guild.id).first()
            )
            if not existing_guild:
                discord_guild_record = models.DiscordGuild(
                    id=guild.id, name=guild.name, create_at=guild.created_at
                )
                session.add(discord_guild_record)
                print(f"✅ Guild '{guild.name}' ({guild.id}) guardado.")
            else:
                print(f"⏩ Guild '{guild.name}' ({guild.id}) ya existe. Saltando.")
        session.commit()





    async def save_user_data(self, session):
        print("\n👤 Guardando información de usuarios:")
        for guild in self.guilds:
            print(f"  📝 Procesando miembros del servidor: {guild.name} ({guild.id})")
            async for member in guild.fetch_members(limit=None):
                existing_user = (
                    session.query(models.DiscordUser)
                    .filter_by(id=member.id, guild_id=guild.id)
                    .first()
                )
                if not existing_user:
                    discord_user_record = models.DiscordUser(
                        id=member.id,
                        name=member.display_name,
                        guild_id=guild.id,
                        joined_at=member.joined_at,
                    )
                    session.add(discord_user_record)
                    print(
                        f"    ✅ Usuario '{member.display_name}' ({member.id}) del guild '{guild.name}' guardado."
                    )
                else:
                    print(
                        f"    ⏩ Usuario '{member.display_name}' ({member.id}) del guild '{guild.name}' ya existe. Saltando."
                    )
            session.commit()





    async def save_channel_data(self, session):
        print("\n📺 Guardando información de canales:")
        for guild in self.guilds:
            print(f"  📝 Procesando canales del servidor: {guild.name} ({guild.id})")
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel) or isinstance(
                    channel, discord.CategoryChannel
                ):  # Only save text channels and categories
                    existing_channel = (
                        session.query(models.DiscordChannel)
                        .filter_by(id=channel.id, guild_id=guild.id)
                        .first()
                    )
                    if not existing_channel:
                        discord_channel_record = models.DiscordChannel(
                            id=channel.id,
                            guild_id=guild.id,
                            name=channel.name,
                            parent_channel_id=channel.category_id
                            if isinstance(channel, discord.TextChannel)
                            and channel.category
                            else None,
                            create_at=channel.created_at,
                            last_messages_at=None,  # This can be updated later if needed
                        )
                        session.add(discord_channel_record)
                        print(
                            f"    ✅ Canal '{channel.name}' ({channel.id}) del guild '{guild.name}' guardado."
                        )
                    else:
                        print(
                            f"    ⏩ Canal '{channel.name}' ({channel.id}) del guild '{guild.name}' ya existe. Saltando."
                        )
            session.commit()

    async def get_discord_channel_history(self, session, guild_id: int, chann_id: int):
        print(
            f"\n📜 Obteniendo historial del canal {chann_id} en el servidor {guild_id}:"
        )
        guild = self.get_guild(guild_id)
        if not guild:
            print(f"❌ Servidor con ID '{guild_id}' no encontrado.")
            return

        channel = guild.get_channel(chann_id)
        if not channel:
            print(f"❌ Canal con ID '{chann_id}' no encontrado.")
            return

        if not isinstance(channel, discord.TextChannel):
            print(f"❌ Canal con ID '{chann_id}' no es un canal de texto.")
            return

        count = 0
        async for msg in channel.history(limit=None, oldest_first=True):
            # evitar guardar mensajes duplicados
            exists = (
                session.query(models.DiscordMessage.id).filter_by(id=msg.id).first()
            )
            if exists:
                continue

            # extraer attachments
            attachments = [
                {"filename": a.filename, "url": a.url, "size": a.size}
                for a in msg.attachments
            ]

            discord_message_record = models.DiscordMessage(
                id=msg.id,
                guild_id=guild.id,
                channel_id=channel.id,
                author_id=msg.author.id,
                content=msg.content if msg.content else None,
                reply_to=msg.reference.message_id if msg.reference else None,
                attachments=attachments if attachments else None,
                message_create_at=msg.created_at,
            )

            session.add(discord_message_record)
            count += 1
            # commit por bloques para no consumir mucha memoria
            if count % 500 == 0:
                session.commit()
                print(f"{count} mensajes guardados...")

        session.commit()
        print(f"✅ {count} mensajes insertados")




if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    # intents.members = True  # Necesario para fetch_members TODO: aparentemente el token no tiene los permisos necesarios, esto genera un error
    intents.messages = True

    # Puedes dejar GUILD_ID y CHANNEL_ID como None para solo guardar la info de los servers, usuarios y canales
    GUILD_ID = 1308885706621452369 # Sun Factory
    CHANNEL_ID = 1357437165738393822

    bot = DiscordEchoSaverBot(intents=intents, guild_id=GUILD_ID, channel_id=CHANNEL_ID)
    if settings.DISCORD_BOT_TOKEN is not None:
        bot.run(settings.DISCORD_BOT_TOKEN)
    else:
        print("❌ DISCORD_BOT_TOKEN no está configurado.")



"""
python3 -m src.apps.DiscordEchoSaver.botv2

"""