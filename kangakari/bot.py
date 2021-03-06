from __future__ import annotations

import logging
import traceback

import hikari
import lightbulb
import msgpack
import sake
from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from kangakari import Config
from kangakari import Database

log = logging.getLogger(__name__)


bot = lightbulb.BotApp(
    Config.TOKEN,
    ignore_bots=True,
    owner_ids=Config.OWNER_IDS,
    default_enabled_guilds=Config.TEST_GUILD_ID,  # this is temporary
    case_insensitive_prefix_commands=True,
    intents=hikari.Intents.ALL,
)

fh = logging.FileHandler("./data/logs/bot.log")
fh.setFormatter(logging.Formatter("%(levelname)-1.1s %(asctime)23.23s %(name)s: %(message)s"))
fh.setLevel(logging.DEBUG)
logging.root.addHandler(fh)


bot.d.scheduler = AsyncIOScheduler()
bot.d.db = Database(Config.POSTGRES_DSN)
bot.d.redis_cache = sake.RedisCache(
    app=bot,
    event_manager=bot.event_manager,
    address=Config.REDIS_ADDRESS,
    password=Config.REDIS_PASSWORD,
    event_managed=True,
    dumps=msgpack.dumps,
    loads=msgpack.loads,
)


bot.load_extensions_from("./kangakari/extensions")


@bot.listen(hikari.StartingEvent)
async def on_starting(_: hikari.StartingEvent) -> None:
    bot.d.scheduler.start()
    bot.d.session = ClientSession()
    log.info("AIOHTTP session created")

    await bot.d.db.connect()
    await bot.d.redis_cache.open()


@bot.listen(hikari.StartedEvent)
async def on_started(_: hikari.StartedEvent) -> None:
    await bot.d.db.build()


@bot.listen(hikari.StoppingEvent)
async def on_stopping(_: hikari.StoppingEvent) -> None:
    await bot.d.db.close()
    await bot.d.session.close()
    log.info("AIOHTTP session closed")
    bot.d.scheduler.shutdown()


@bot.listen(lightbulb.CommandErrorEvent)
async def on_command_error(e: lightbulb.CommandErrorEvent) -> None:
    # exc = getattr(e.exception, "__cause__", e.exception)
    exc_info = e.exc_info

    # handle errors

    log.error("An unhandled exception occurred executing a command (%s)", e.context.command.name, exc_info=exc_info)

    error_id = await bot.d.db.fetch_val(
        "INSERT INTO errors (message) VALUES ($1) RETURNING error_id",
        "".join(traceback.format_exception(*exc_info)),
    )

    await e.context.respond(
        f"An error occurred. Please contact {' | '.join(f'<@{owner_id}>' for owner_id in Config.OWNER_IDS)}"
        f" with this ID: `{error_id}`.",
    )


def run() -> None:
    # lavasnek_rs doesn't work with uvloop
    # if os.name != "nt":
    #    import uvloop
    #
    #    uvloop.install()
    bot.run(asyncio_debug=True)


__all__ = ["run"]
