import discord
from typing import Optional
from src import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src import models
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


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
        logging.info(f"🤖 Conectado como {self.user}")
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            # Check if database is empty
            if self._is_database_empty(session):
                logging.info(
                    "La base de datos está vacía. Realizando extracción completa."
                )
                await self.perform_full_extraction(session)
            else:
                logging.info(
                    "La base de datos contiene datos. Realizando extracción incremental."
                )
                await self.perform_incremental_extraction(session)
        except SQLAlchemyError as e:
            logging.error(f"Error de base de datos durante la operación: {e}")
            session.rollback()
        except Exception as e:
            logging.error(f"Error inesperado: {e}")
        finally:
            session.close()
            await self.close()

    def _is_database_empty(self, session) -> bool:
        return session.query(models.DiscordGuild).first() is None

    async def perform_full_extraction(self, session):
        await self.save_guild_data(session)
        await self.save_user_data(session)
        await self.save_channel_data(session)
        await self.save_all_channel_messages(session)

    async def perform_incremental_extraction(self, session):
        await self.save_guild_data(
            session
        )  # This method already handles incremental updates
        await self.save_user_data(
            session
        )  # This method already handles incremental updates
        await self.save_channel_data(
            session
        )  # This method already handles incremental updates
        await self.update_new_channel_messages(session)

    async def save_guild_data(self, session):
        logging.info("\n📦 Guardando información de servidores:")
        for guild in self.guilds:
            existing_guild = (
                session.query(models.DiscordGuild).filter_by(id=guild.id).first()
            )
            if not existing_guild:
                discord_guild_record = models.DiscordGuild(
                    id=guild.id, name=guild.name, create_at=guild.created_at
                )
                session.add(discord_guild_record)
                logging.info(f"✅ Guild '{guild.name}' ({guild.id}) guardado.")
            else:
                logging.info(
                    f"⏩ Guild '{guild.name}' ({guild.id}) ya existe. Saltando."
                )
        session.commit()

    async def save_user_data(self, session):
        logging.info("\n👤 Guardando información de usuarios:")
        for guild in self.guilds:
            logging.info(
                f"  📝 Procesando miembros del servidor: {guild.name} ({guild.id})"
            )
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
                    logging.info(
                        f"    ✅ Usuario '{member.display_name}' ({member.id}) del guild '{guild.name}' guardado."
                    )
                else:
                    logging.info(
                        f"    ⏩ Usuario '{member.display_name}' ({member.id}) del guild '{guild.name}' ya existe. Saltando."
                    )
            session.commit()

    async def save_channel_data(self, session):
        logging.info("\n📺 Guardando información de canales:")
        for guild in self.guilds:
            logging.info(
                f"  📝 Procesando canales del servidor: {guild.name} ({guild.id})"
            )
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
                            parent_channel_id=(
                                channel.category_id
                                if isinstance(channel, discord.TextChannel)
                                and channel.category
                                else None
                            ),
                            create_at=channel.created_at,
                            last_messages_at=None,  # This can be updated later if needed
                        )
                        session.add(discord_channel_record)
                        logging.info(
                            f"    ✅ Canal '{channel.name}' ({channel.id}) del guild '{guild.name}' guardado."
                        )
                    else:
                        logging.info(
                            f"    ⏩ Canal '{channel.name}' ({channel.id}) del guild '{guild.name}' ya existe. Saltando."
                        )
            session.commit()

    async def save_all_channel_messages(self, session):
        logging.info("\n📜 Obteniendo historial de mensajes de todos los canales:")
        for guild in self.guilds:
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    logging.info(
                        f"  📝 Procesando mensajes del canal: {channel.name} ({channel.id}) en el servidor {guild.name}"
                    )
                    await self._get_and_save_messages(session, channel)

    async def update_new_channel_messages(self, session):
        logging.info("\n📜 Actualizando nuevos mensajes de canales existentes:")
        for guild in self.guilds:
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    db_channel = (
                        session.query(models.DiscordChannel)
                        .filter_by(id=channel.id, guild_id=guild.id)
                        .first()
                    )
                    if db_channel and db_channel.last_messages_at:
                        logging.info(
                            f"  📝 Procesando nuevos mensajes del canal: {channel.name} ({channel.id}) desde {db_channel.last_messages_at}"
                        )
                        await self._get_and_save_messages(
                            session, channel, after=db_channel.last_messages_at
                        )
                    else:
                        logging.info(
                            f"  ⏩ Canal '{channel.name}' ({channel.id}) sin 'last_messages_at' o no encontrado. Realizando extracción completa de este canal."
                        )
                        await self._get_and_save_messages(session, channel)

    async def _get_channels_by_ids(
        self, guild: discord.Guild, channel_ids: list[int]
    ) -> list[discord.TextChannel]:
        channels = []
        for chann_id in channel_ids:
            channel = guild.get_channel(chann_id)
            if not channel:
                logging.warning(
                    f"❌ Canal con ID '{chann_id}' no encontrado en el servidor '{guild.name}'. Saltando."
                )
                continue
            if not isinstance(channel, discord.TextChannel):
                logging.warning(
                    f"❌ Canal con ID '{chann_id}' no es un canal de texto en el servidor '{guild.name}'. Saltando."
                )
                continue
            channels.append(channel)
        return channels

    async def save_specific_channels_full_history(
        self, session, guild_id: int, channel_ids: list[int]
    ):
        logging.info(
            f"\n📜 Obteniendo historial completo de mensajes de canales específicos en el servidor {guild_id}:"
        )
        guild = self.get_guild(guild_id)
        if not guild:
            logging.error(
                f"❌ Servidor con ID '{guild_id}' no encontrado. No se pueden extraer mensajes de canales específicos."
            )
            return

        channels_to_process = await self._get_channels_by_ids(guild, channel_ids)
        for channel in channels_to_process:
            logging.info(
                f"  📝 Procesando historial completo del canal: {channel.name} ({channel.id}) en el servidor {guild.name}"
            )
            await self._get_and_save_messages(session, channel)

    async def update_specific_channels_new_messages(
        self, session, guild_id: int, channel_ids: list[int]
    ):
        logging.info(
            f"\n📜 Actualizando nuevos mensajes de canales específicos en el servidor {guild_id}:"
        )
        guild = self.get_guild(guild_id)
        if not guild:
            logging.error(
                f"❌ Servidor con ID '{guild_id}' no encontrado. No se pueden extraer nuevos mensajes de canales específicos."
            )
            return

        channels_to_process = await self._get_channels_by_ids(guild, channel_ids)
        for channel in channels_to_process:
            db_channel = (
                session.query(models.DiscordChannel)
                .filter_by(id=channel.id, guild_id=guild.id)
                .first()
            )
            if db_channel and db_channel.last_messages_at:
                logging.info(
                    f"  📝 Procesando nuevos mensajes del canal: {channel.name} ({channel.id}) desde {db_channel.last_messages_at}"
                )
                await self._get_and_save_messages(
                    session, channel, after=db_channel.last_messages_at
                )
            else:
                logging.info(
                    f"  ⏩ Canal '{channel.name}' ({channel.id}) sin 'last_messages_at' o no encontrado en la DB. Realizando extracción completa de este canal."
                )
                await self._get_and_save_messages(session, channel)

    async def _get_and_save_messages(
        self, session, channel: discord.TextChannel, after=None
    ):
        count = 0
        latest_message_timestamp = None
        try:
            async for msg in channel.history(
                limit=None, oldest_first=True, after=after
            ):
                exists = (
                    session.query(models.DiscordMessage.id).filter_by(id=msg.id).first()
                )
                if exists:
                    continue

                attachments = [
                    {"filename": a.filename, "url": a.url, "size": a.size}
                    for a in msg.attachments
                ]

                discord_message_record = models.DiscordMessage(
                    id=msg.id,
                    guild_id=channel.guild.id,
                    channel_id=channel.id,
                    author_id=msg.author.id,
                    content=msg.content if msg.content else None,
                    reply_to=msg.reference.message_id if msg.reference else None,
                    attachments=attachments if attachments else None,
                    message_create_at=msg.created_at,
                )

                session.add(discord_message_record)
                count += 1
                latest_message_timestamp = (
                    msg.created_at
                )  # Update timestamp for each message
                if count % 500 == 0:
                    session.commit()
                    logging.info(
                        f"{count} mensajes guardados para el canal '{channel.name}'..."
                    )

            session.commit()
            logging.info(
                f"✅ {count} mensajes insertados/actualizados para el canal '{channel.name}'."
            )

            # Update last_messages_at for the channel if new messages were saved
            if latest_message_timestamp:
                db_channel = (
                    session.query(models.DiscordChannel)
                    .filter_by(id=channel.id, guild_id=channel.guild.id)
                    .first()
                )
                if db_channel:
                    db_channel.last_messages_at = latest_message_timestamp
                    session.add(db_channel)
                    session.commit()
                    logging.info(
                        f"🕒 'last_messages_at' actualizado para el canal '{channel.name}' a {latest_message_timestamp}."
                    )

        except discord.Forbidden:
            logging.warning(
                f"⚠️ No tengo permisos para leer el historial de mensajes en el canal '{channel.name}' ({channel.id}). Saltando."
            )
            session.rollback()  # Rollback any partial commits for this channel
        except Exception as e:
            logging.error(
                f"Error al obtener mensajes del canal '{channel.name}' ({channel.id}): {e}"
            )
            session.rollback()  # Rollback any partial commits for this channel


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    intents.messages = True

    # GUILD_ID y CHANNEL_ID are no longer directly used for full/incremental extraction logic,
    # but kept for potential specific channel history retrieval if needed.
    GUILD_ID = None
    CHANNEL_ID = None

    bot = DiscordEchoSaverBot(intents=intents, guild_id=GUILD_ID, channel_id=CHANNEL_ID)
    if settings.DISCORD_BOT_TOKEN is not None:
        bot.run(settings.DISCORD_BOT_TOKEN)
    else:
        logging.error("❌ DISCORD_BOT_TOKEN no está configurado.")
