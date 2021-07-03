import asyncio
import logging
import os
import typing as t
from functools import wraps

import aiofiles
import asyncpg
import lightbulb


def acquire(func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
    @wraps(func)
    async def wrapper(self: "Database", *args: t.Any, **kwargs: t.Any) -> t.Any:
        assert self.is_connected, "Not connected."
        cxn: asyncpg.Connection
        async with self._pool.acquire() as cxn:
            async with cxn.transaction():
                return await func(self, *args, _cxn=cxn, **kwargs)

    return wrapper


class Database:
    __slots__: t.Sequence[str] = ("bot", "_connected", "_pool")

    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot: lightbulb.Bot = bot
        self._connected = asyncio.Event()

    async def wait_until_connected(self) -> None:
        await self._connected.wait()

    @property
    def is_connected(self) -> bool:
        return self._connected.is_set()

    async def connect(self) -> None:
        assert not self.is_connected, "Already connected."
        self._pool: asyncpg.Pool = await asyncpg.create_pool(dsn=self.bot.config.DB_DSN)
        self._connected.set()
        logging.info("Connected to database.")

        await self.sync()

    async def close(self) -> None:
        assert self.is_connected, "Not connected."
        await self._pool.close()
        self._connected.clear()
        logging.info("Closed database connection.")

    async def sync(self) -> None:
        await self.execute_script(os.path.join(self.bot._static, "script.sql"), self.bot.config.DEFAULT_PREFIX)
        await self.execute_many(
            "INSERT INTO guilds (guildid) VALUES ($1) ON CONFLICT DO NOTHING",
            [(guild,) for guild in self.bot.cache.get_available_guilds_view()],
        )
        stored = [guild_id for guild_id in await self.column("SELECT guildid FROM guilds")]
        member_of = self.bot.cache.get_available_guilds_view()
        to_remove = [(guild_id,) for guild_id in set(stored) - set(member_of)]
        await self.execute_many("DELETE FROM guilds WHERE guildid = $1;", to_remove)

        logging.info("Synchronised database.")

    @acquire
    async def execute(self, query: str, *values: t.Any, _cxn: asyncpg.Connection) -> None:
        await _cxn.execute(query, *values)

    @acquire
    async def execute_many(self, query: str, valueset: t.List[t.Any], _cxn: asyncpg.Connection) -> None:
        await _cxn.executemany(query, valueset)

    @acquire
    async def val(self, query: str, *values: t.Any, column: int = 0, _cxn: asyncpg.Connection) -> t.Any:
        return await _cxn.fetchval(query, *values, column=column)

    @acquire
    async def column(self, query: str, *values: t.Any, column: int = 0, _cxn: asyncpg.Connection) -> t.List[t.Any]:
        return [record[column] for record in await _cxn.fetch(query, *values)]

    @acquire
    async def row(self, query: str, *values: t.Any, _cxn: asyncpg.Connection) -> t.List[t.Any]:
        return await _cxn.fetchrow(query=query, *values)

    @acquire
    async def all(self, query: str, *values: t.Any, _cxn: asyncpg.Connection) -> t.List[asyncpg.Record]:
        return await _cxn.fetch(query, *values)

    @acquire
    async def execute_script(self, path: str, *args: t.Any, _cxn: asyncpg.Connection) -> None:
        async with aiofiles.open(path, "r") as script:
            await _cxn.execute((await script.read()).format(*args))


__all__: t.Sequence[str] = ["Database"]
