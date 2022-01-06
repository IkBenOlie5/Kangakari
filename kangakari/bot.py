from __future__ import annotations

import logging
import os
import traceback

import hikari
import lightbulb
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


bot.d.scheduler = AsyncIOScheduler()
bot.d.db = Database(Config.POSTGRES_DSN)
bot.d.redis_cache = sake.RedisCache(
    app=bot, event_manager=bot.event_manager, address=Config.REDIS_ADDRESS, password=Config.REDIS_PASSWORD
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
    exc = getattr(e.exception, "__cause__", e.exception)

    # handle errors

    message = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    log.error(message)

    error_id = await bot.d.db.fetch_val(
        "INSERT INTO errors (message) VALUES ($1) RETURNING error_id",
        message,
    )

    await e.context.respond(
        f"An error occurred. Please contact {' | '.join(f'<@{owner_id}>' for owner_id in Config.OWNER_IDS)}"
        f" with this ID: `{error_id}`.",
    )


def run() -> None:
    if os.name != "nt":
        import uvloop

        uvloop.install()
    bot.run(asyncio_debug=True)


__all__ = ["run"]
