
import discord
from src import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src import models


class DiscordEchoSaverBot(discord.Client):
    def __init__(self, guild_id: int, channel_id: int, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.engine = create_engine(settings.APP_CONN_STRING)
        self.guild_id = guild_id
        self.channel_id = channel_id

    async def on_ready(self):
        print(f"🤖 Conectado como {self.user}")
        # await self.list_all_users()
        # await self.list_guilds()
        # await self.list_channels(self.guild_id)
        await self.get_discord_channel_history(self.guild_id, self.channel_id)




    async def list_guilds(self):
        print("\n📦 Servidores accesibles por el bot:\n")
        for guild in self.guilds:
            print(f"✅ {guild.name} | ID: {guild.id}")




    async def list_channels(self, guild_id: int):
        guild = self.get_guild(guild_id)
        if not guild:
            print("❌ Guild no encontrado")
            return
        print(f"\n📦 Servidor: {guild.name}\n")
        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if perms.read_messages and perms.read_message_history:
                print(f"✅ {channel.name} | ID: {channel.id}")
            else:
                print(f"🔒 {channel.name} | SIN PERMISOS")
    

    async def list_all_users(self):

        for guild in self.guilds:

            print(f"\n📦 Servidor: {guild.name} ({guild.id})")

            async for member in guild.fetch_members(limit=None):

                print(
                    f"👤 {member.display_name} | "
                    f"username: {member.name} | "
                    f"id: {member.id}"
                )




    async def get_discord_channel_history(self, guild_id: int, chann_id: int):

        Session = sessionmaker(bind=self.engine)
        session = Session()

        guild = self.get_guild(guild_id)
        if not guild:
            print(f"❌ Servidor con ID '{guild_id}' no encontrado.")
            await self.close()
            return

        channel = guild.get_channel(chann_id)
        if not channel:
            print(f"❌ Canal con ID '{chann_id}' no encontrado.")
            await self.close()
            return

        if not isinstance(channel, discord.TextChannel):
            print(f"❌ Canal con ID '{chann_id}' no es un canal de texto.")
            await self.close()
            return

        count = 0
        async for msg in channel.history(limit=None, oldest_first=True):
            # evitar guardar mensajes duplicados
            exists = session.query(models.DiscordMessage.id).filter_by(
                discord_message_id=msg.id
            ).first()
            if exists:
                continue

            # extraer attachments
            attachments = [
                {
                    "filename": a.filename,
                    "url": a.url,
                    "size": a.size
                }
                for a in msg.attachments
            ]

            discord_message_record = models.DiscordMessage(

                discord_message_id=msg.id,

                guild_id=guild.id,
                guild_name=guild.name,

                channel_id=channel.id,
                channel_name=channel.name,

                author_id=msg.author.id,
                author_name=msg.author.display_name,

                content=msg.content if msg.content else None,

                reply_to=msg.reference.message_id if msg.reference else None,

                attachments=attachments if attachments else None,

                message_create_at=msg.created_at,
                edited_at=msg.edited_at

                #is_bot=msg.author.bot
            )

            session.add(discord_message_record)
            count += 1
            # commit por bloques para no consumir mucha memoria
            if count % 500 == 0:
                session.commit()
                print(f"{count} mensajes guardados...")

        session.commit()

        print(f"✅ {count} mensajes insertados")

        await self.close()




if __name__ == "__main__":

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.messages = True
    intents.members = True


    GUILD_ID = 1308885706621452369 # Sun Factory
    GUILD_ID = 772855809406271508 # Unergy

    CHANNEL_ID = 1357437165738393822 

    bot = DiscordEchoSaverBot(GUILD_ID, CHANNEL_ID, intents=intents)
    bot.run(settings.DISCORD_BOT_TOKEN)



"""
python3 -m src.apps.DiscordEchoSaver.botv1

"""