import logging
import typing as t
from pathlib import Path

import hikari
import lightbulb
import sake
from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from kangakari import Config
from kangakari.core.db import Database
from kangakari.core.utils import Context
from kangakari.core.utils import Embeds
from kangakari.core.utils import Help


class RedisCache(sake.redis.PrefixCache, sake.redis.RedisCache):
    pass


class Bot(lightbulb.Bot):
    def __init__(self, version: str) -> None:
        self._plugins = [p.stem for p in Path(".").glob("./kangakari/core/plugins/*.py")]
        self._dynamic = "./kangakari/data/dynamic"
        self._static = "./kangakari/data/static"

        self.version = version
        self.config = Config()

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

        self.setup_logger()

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

        self.scheduler = AsyncIOScheduler()
        self.db = Database(self)
        self.embeds = Embeds()
        self.redis_cache = RedisCache(
            self, self, address=self.config.REDIS_ADDRESS, password=self.config.REDIS_PASSWORD, ssl=False
        )

    def get_context(self, *args: t.Any, **kwargs: t.Any) -> Context:
        return Context(self, *args, **kwargs)

    def setup_logger(self) -> None:
        self.log = logging.getLogger("root")
        self.log.setLevel(logging.INFO)

        file_handler = logging.handlers.TimedRotatingFileHandler(  # type: ignore
            "./kangakari/data/logs/main.log", when="D", interval=3, encoding="utf-8", backupCount=10
        )

        formatter = logging.Formatter("%(levelname)-1.1s %(asctime)23.23s %(name)s: %(message)s")
        file_handler.setFormatter(formatter)
        self.log.addHandler(file_handler)

    async def on_starting(self, _: hikari.StartingEvent) -> None:
        self.session = ClientSession()
        await self.db.connect()
        await self.redis_cache.open()

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

    async def resolve_prefix(self, _: lightbulb.Bot, message: hikari.Message) -> t.Union[t.Sequence[str], str]:
        if message.guild_id is None:
            return self.config.DEFAULT_PREFIX
        try:
            prefixes = await self.redis_cache.get_prefixes(message.guild_id)
        except sake.errors.EntryNotFound:
            prefixes = await self.db.column("SELECT prefix FROM prefixes WHERE guildid = $1", message.guild_id)
            await self.redis_cache.set_prefixes(
                message.guild_id,
                prefixes,
            )
        return prefixes

    async def on_guild_available(self, event: hikari.GuildAvailableEvent) -> None:
        await self.db.wait_until_connected()
        await self.db.execute("INSERT INTO prefixes (guildid) VALUES ($1) ON CONFLICT DO NOTHING", event.guild_id)

    async def on_guild_leave(self, event: hikari.GuildLeaveEvent) -> None:
        await self.db.wait_until_connected()
        await self.db.execute("DELETE FROM prefixes WHERE guildid = $1", event.guild_id)

    async def on_guild_message_create(self, event: hikari.GuildMessageCreateEvent) -> None:
        """await self.db.wait_until_connected()
        if not event.author_id == self.me.id:
            await self.db.execute("INSERT INTO users (userid) VALUES ($1) ON CONFLICT DO NOTHING", event.author_id)"""
