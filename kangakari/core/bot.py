import logging
import typing
from pathlib import Path

import lavasnek_rs
import lightbulb
from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from hikari import Intents
from hikari import events
from sake import redis
from sake.errors import EntryNotFound

from kangakari.core.plugins.music import EventHandler
from kangakari.utils import Config
from kangakari.utils import Context
from kangakari.utils import Database
from kangakari.utils import Embeds
from kangakari.utils import Help

if typing.TYPE_CHECKING:
    from hikari import Message


class RedisCache(redis.PrefixCache, redis.RedisCache):
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
            intents=Intents.ALL,
            prefix=lightbulb.when_mentioned_or(self.resolve_prefix),
            insensitive_commands=True,
            ignore_bots=True,
            logs=self.config.LOG_LEVEL,
            help_class=Help,
        )

        self.setup_logger()

        subscriptions = {
            events.StartingEvent: self.on_starting,
            events.StartedEvent: self.on_started,
            events.StoppingEvent: self.on_stopping,
            events.GuildAvailableEvent: self.on_guild_available,
            events.GuildLeaveEvent: self.on_guild_leave,
            events.GuildMessageCreateEvent: self.on_guild_message_create,
        }
        for e, c in subscriptions.items():
            self.event_manager.subscribe(e, c)

        self.scheduler = AsyncIOScheduler()
        self.db = Database(self)
        self.embeds = Embeds()
        self.redis_cache = RedisCache(
            self,
            self,
            address=self.config.REDIS_ADDRESS,
            password=self.config.REDIS_PASSWORD,
            ssl=False,
        )
        self.lavalink: typing.Optional[lavasnek_rs.Lavalink] = None

    def get_context(self, *args: typing.Any, **kwargs: typing.Any) -> Context:
        return Context(self, *args, **kwargs)

    def setup_logger(self) -> None:
        self.log = logging.getLogger("root")
        self.log.setLevel(logging.INFO)

        file_handler = logging.handlers.TimedRotatingFileHandler(  # type: ignore
            "./kangakari/data/logs/main.log",
            when="D",
            interval=3,
            encoding="utf-8",
            backupCount=10,
        )

        formatter = logging.Formatter("%(levelname)-1.1s %(asctime)23.23s %(name)s: %(message)s")
        file_handler.setFormatter(formatter)
        self.log.addHandler(file_handler)

    async def on_starting(self, _: events.StartingEvent) -> None:
        self.session = ClientSession()
        await self.db.connect()
        await self.redis_cache.open()

        for plugin in self._plugins:
            try:
                self.load_extension(f"kangakari.core.plugins.{plugin}")
                logging.info(f"Plugin '{plugin}' has been loaded.")
            except lightbulb.errors.ExtensionMissingLoad:
                logging.error(f"Plugin '{plugin}' is missing a load function.")

    async def on_started(self, _: events.StartedEvent) -> None:
        self.scheduler.start()

        builder = (
            lavasnek_rs.LavalinkBuilder(self.get_me().id, self.config.TOKEN)
            .set_host("127.0.0.1")
            .set_password(self.config.LAVALINK_PASSWORD)
        )
        self.lavalink = await builder.build(EventHandler())

    async def on_stopping(self, _: events.StoppingEvent) -> None:
        self.scheduler.shutdown()
        await self.db.close()
        await self.session.close()
        logging.info("Closed aiohttp session.")

    async def resolve_prefix(self, _: lightbulb.Bot, message: "Message") -> typing.Union[typing.Sequence[str], str]:
        if message.guild_id is None:
            return self.config.DEFAULT_PREFIX
        try:
            prefixes = await self.redis_cache.get_prefixes(message.guild_id)
        except EntryNotFound:
            prefixes = await self.db.val("SELECT prefixes FROM guilds WHERE guild_id = $1", message.guild_id)
            await self.redis_cache.set_prefixes(
                message.guild_id,
                prefixes,
            )
        return prefixes

    async def on_guild_available(self, e: events.GuildAvailableEvent) -> None:
        await self.db.wait_until_connected()
        await self.db.execute(
            "INSERT INTO guilds (guild_id) VALUES ($1) ON CONFLICT DO NOTHING",
            e.guild_id,
        )

    async def on_guild_leave(self, e: events.GuildLeaveEvent) -> None:
        await self.db.wait_until_connected()
        await self.db.execute("DELETE FROM guilds WHERE guild_id = $1", e.guild_id)

    async def on_guild_message_create(self, e: events.GuildMessageCreateEvent) -> None:
        """await self.db.wait_until_connected()
        if not e.author_id == self.me.id:
            await self.db.execute("INSERT INTO users (user_id) VALUES ($1) ON CONFLICT DO NOTHING", e.author_id)"""
