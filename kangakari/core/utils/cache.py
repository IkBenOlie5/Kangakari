import json
import typing
from enum import IntEnum

from hikari import snowflakes
from sake import errors
from sake import redis
from sake import redis_iterators
from sake import traits


class ResourceIndex(IntEnum):
    PREFIX = 12


class PrefixCache(redis.ResourceClient):
    @classmethod
    def index(cls) -> typing.Sequence[int]:
        return (ResourceIndex.PREFIX,)

    async def clear_prefixes(self) -> None:
        client = self.get_connection(ResourceIndex.PREFIX)
        await client.fushdb()

    async def delete_prefixes(self, guild_id: snowflakes.Snowflakeish, /) -> None:
        client = self.get_connection(ResourceIndex.PREFIX)
        await client.delete(int(guild_id))

    async def get_prefixes(self, guild_id: snowflakes.Snowflakeish, /) -> typing.Sequence[str]:
        guild_id = int(guild_id)
        client = self.get_connection(ResourceIndex.PREFIX)
        data = await client.get(guild_id)

        if not data:
            raise errors.EntryNotFound(f"Prefix entry `{guild_id}` not found")

        return json.loads(data)

    async def iter_prefixes(
        self, *, window_size: int = redis.WINDOW_SIZE
    ) -> traits.CacheIterator[typing.Sequence[str]]:
        return redis_iterators.Iterator(self, ResourceIndex.PREFIX, json.loads, window_size=window_size)

    async def set_prefixes(self, guild_id: snowflakes.Snowflakeish, prefixes: typing.Sequence[str], /) -> None:
        client = self.get_connection(ResourceIndex.PREFIX)
        data = json.dumps(prefixes)
        await client.set(int(guild_id), data)


class RedisCache(redis.RedisCache, PrefixCache):
    pass
