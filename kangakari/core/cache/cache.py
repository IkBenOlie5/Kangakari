import asyncio
import logging
import types
import typing as t

import aiomcache
import msgpack
from lightbulb import Bot

ExpireT = t.Union[int, float]


def to_bytes(value: t.Any) -> bytes:
    return f"{value}".encode("utf-8")


class Cache:
    __slots__: t.Sequence[str] = ("bot", "_connected", "_client")

    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
        self._connected = asyncio.Event()

    async def wait_until_connected(self):
        await self._connected.wait()

    @property
    def is_connected(self):
        return self._connected.is_set()

    async def connect(self) -> None:
        assert not self.is_connected, "Already connected."
        self._client: aiomcache.Client = aiomcache.Client(self.bot.config.CACHE_HOST, self.bot.config.CACHE_PORT)
        self._connected.set()
        logging.info("Connected to cache.")

    async def get(self, key: t.Any) -> t.Any:
        assert self.is_connected, "Not connected."
        key_bytes: bytes = to_bytes(key)
        value: bytes = await self._client.get(key_bytes)
        if value is not None:
            return msgpack.loads(value)

    async def get_many(self, keys: t.List[t.Any]) -> t.AsyncGenerator[t.Any, None]:
        assert self.is_connected, "Not connected."
        keys_bytes: t.List[bytes] = [to_bytes(key) for key in keys]
        value: bytes
        for value in await self._client.multi_get(*keys_bytes):
            if value is None:
                yield value
            else:
                yield msgpack.loads(value)

    async def set(self, key: t.Any, value: t.Any, *, expire: ExpireT = 0) -> None:
        assert self.is_connected, "Not connected."
        key_bytes: bytes = to_bytes(key)
        value_bytes: bytes = msgpack.dumps(value)
        await self._client.set(key_bytes, value_bytes, exptime=expire)

    async def set_many(self, pairs: t.List[t.Tuple[t.Any, t.Any]], *, expire: ExpireT = 0) -> None:
        assert self.is_connected, "Not connected."
        key: t.Any
        value: t.Any
        for key, value in pairs:
            await self.set(key, value, expire=expire)

    async def add(self, key: t.Any, value: t.Any, *, expire: ExpireT = 0) -> None:
        assert self.is_connected, "Not connected."
        if await self.exists(key):
            raise ValueError(f"Key {key} already in cache.")
        await self.set(key, value, expire=expire)

    async def exists(self, key: t.Any) -> bool:
        assert self.is_connected, "Not connected."
        key_bytes: bytes = to_bytes(key)
        return bool(await self._client.append(key_bytes, b""))

    async def delete(self, key: t.Any) -> None:
        assert self.is_connected, "Not connected."
        key_bytes: bytes = to_bytes(key)
        await self._client.delete(key_bytes)

    async def clear(self) -> None:
        assert self.is_connected, "Not connected."
        await self._client.flush_all()

    async def close(self) -> None:
        assert self.is_connected, "Not connected."
        await self._client.close()
        self._connected.clear()
        logging.info("Closed cache connection.")

    async def __aenter__(self) -> "Cache":
        self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: t.Type[t.Type[BaseException]],
        exc_val: t.Type[BaseException],
        exc_tb: t.Type[types.TracebackType],
    ) -> None:
        await self.close()


__all__: t.Sequence[str] = "Cache"
