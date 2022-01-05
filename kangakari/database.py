from __future__ import annotations

import logging
import typing as t
from contextlib import asynccontextmanager

import aiofiles
import asyncpg
import hikari

log = logging.getLogger(__name__)


@asynccontextmanager
async def _acquire(pool: asyncpg.Pool) -> asyncpg.Connection:
    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                yield conn
    finally:
        pass


class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self._pool = None

    async def connect(self) -> None:
        self._pool = await asyncpg.create_pool(self.dsn)
        log.info("Connected to database")

    async def close(self) -> None:
        assert self._pool is not None
        await self._pool.close()
        log.info("Closed database pool")

    async def sync(self, guilds: list[hikari.Guild], default_prefix: str) -> None:
        async with aiofiles.open("./data/build.sql") as f:
            await self.execute((await f.read()) % default_prefix)
        log.info("Built database")

        await self.execute_many(
            "INSERT INTO guilds (guild_id) VALUES ($1) ON CONFLICT DO NOTHING", [(guild,) for guild in guilds]
        )
        stored = [guild_id for guild_id in await self.fetch_column("SELECT guild_id FROM guilds")]
        to_remove = [(guild_id,) for guild_id in set(stored) - set(guilds)]
        await self.execute_many("DELETE FROM guilds WHERE guild_id = $1;", to_remove)

        log.info("Synchronised database")

    async def execute(self, command: str, *args: t.Any) -> None:
        async with _acquire(self._pool) as conn:
            await conn.execute(command, *args)

    async def execute_many(self, command: str, args: list[t.Any]) -> None:
        async with _acquire(self._pool) as conn:
            await conn.executemany(command, args)

    async def fetch_val(self, command: str, *args: t.Any, column: int = 0) -> t.Any:
        async with _acquire(self._pool) as conn:
            return await conn.fetchval(command, *args, column=column)

    async def fetch_column(self, command: str, *args: t.Any, column: int = 0) -> list[t.Any]:
        async with _acquire(self._pool) as conn:
            return [record[column] for record in await conn.fetch(command, *args)]

    async def fetch_record(self, command: str, *args: t.Any) -> asyncpg.Record:
        async with _acquire(self._pool) as conn:
            return await conn.fetchrow(command, *args)

    async def fetch_all(self, command: str, *args: t.Any) -> list[asyncpg.Record]:
        async with _acquire(self._pool) as conn:
            return await conn.fetch(command, *args)


__all__ = ["Database"]
