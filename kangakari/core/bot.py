import logging
from pathlib import Path

import hikari
import lightbulb
from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from kangakari import Config
from kangakari.core.cache import Cache
from kangakari.core.context import Context
from kangakari.core.db import Database
from kangakari.core.help import Help
from kangakari.core.utils import Embeds


class Bot(lightbulb.Bot):
    def __init__(self, version: str) -> None:
        self._plugins = [p.stem for p in Path(".").glob("./kangakari/core/plugins/*.py")]
        self._dynamic = "./kangakari/data/dynamic"
        self._static = "./kangakari/data/static"

        self.version = version

        self.scheduler = AsyncIOScheduler()
        self.config = Config()
        self.db = Database(self)
        self.prefix_cache = Cache(self)
        self.session = ClientSession()
        self.embeds = Embeds()

        self.setup_logger()

        super().__init__(
            token=self.config.TOKEN,
            owner_ids=self.config.OWNER_IDS,
            intents=hikari.Intents.ALL,
            prefix=lightbulb.when_mentioned_or(self.resolve_prefix),
            insensitive_commands=True,
            ignore_bots=True,
            logs=self.config.LOG_LEVEL,
            help_class=Help,
        )

        subscriptions = {
            hikari.StartingEvent: self.on_starting,
            hikari.StartedEvent: self.on_started,
            hikari.StoppingEvent: self.on_stopping,
            hikari.GuildAvailableEvent: self.on_guild_available,
            hikari.GuildLeaveEvent: self.on_guild_leave,
            hikari.GuildMessageCreateEvent: self.on_guild_message_create,
        }
        for e, c in subscriptions.items():
            self.event_manager.subscribe(e, c)

    def get_context(self, *args, **kwargs):
        return Context(self, *args, **kwargs)

    def setup_logger(self):
        self.log = logging.getLogger(self.__class__.__name__)

        file_handler = logging.handlers.TimedRotatingFileHandler("kangakari.log", when="D", interval=7)
        file_handler.setLevel(logging.INFO)
        self.log.addHandler(file_handler)

    async def on_starting(self, _: hikari.StartingEvent) -> None:
        await self.db.connect()
        await self.prefix_cache.connect()

        for plugin in self._plugins:
            try:
                self.load_extension(f"kangakari.core.plugins.{plugin}")
                logging.info(f"Plugin '{plugin}' has been loaded.")
            except lightbulb.errors.ExtensionMissingLoad:
                logging.error(f"Plugin '{plugin}' is missing a load function.")

    async def on_started(self, _: hikari.StartedEvent) -> None:
        self.scheduler.start()

    async def on_stopping(self, _: hikari.StoppingEvent) -> None:
        self.scheduler.shutdown()
        await self.db.close()
        await self.session.close()
        logging.info("Closed aiohttp session.")

    async def resolve_prefix(self, _: lightbulb.Bot, message: hikari.Message) -> str:
        if (prefix := await self.prefix_cache.get(message.guild_id)) is None:
            await self.prefix_cache.set(
                message.guild_id,
                prefix := await self.db.val("SELECT prefix FROM guilds WHERE guildid = $1", message.guild_id),
            )
        return prefix

    async def on_guild_available(self, event: hikari.GuildAvailableEvent):
        await self.db.wait_until_connected()
        await self.db.execute("INSERT INTO guilds (guildid) VALUES ($1) ON CONFLICT DO NOTHING", event.guild_id)

    async def on_guild_leave(self, event: hikari.GuildLeaveEvent):
        await self.db.wait_until_connected()
        await self.db.execute("DELETE FROM guilds WHERE guildid = $1", event.guild_id)

    async def on_guild_message_create(self, event: hikari.GuildMessageCreateEvent):
        await self.db.wait_until_connected()
        await self.db.execute("INSERT INTO users (userid) VALUES ($1) ON CONFLICT DO NOTHING", event.author_id)
