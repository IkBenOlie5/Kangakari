import json
import typing as t
from enum import IntEnum

from hikari import snowflakes
from sake import errors
from sake import redis
from sake import redis_iterators
from sake import traits

# this will no longer be necessary when this gets merged https://github.com/FasterSpeeding/Sake/pull/33


class ResourceIndex(IntEnum):
    PREFIX = 12


class PrefixCache(redis.ResourceClient):
    @classmethod
    def index(cls) -> t.Sequence[ResourceIndex]:
        return (ResourceIndex.PREFIX,)  # type: ignore

    async def clear_prefixes(self) -> None:
        client = self.get_connection(ResourceIndex.PREFIX)  # type: ignore
        await client.flushdb()

    async def delete_prefixes(self, guild_id: snowflakes.Snowflakeish, /) -> None:
        client = self.get_connection(ResourceIndex.PREFIX)  # type: ignore
        await client.delete(int(guild_id))

    async def get_prefixes(self, guild_id: snowflakes.Snowflakeish, /) -> t.Sequence[str]:
        guild_id = int(guild_id)
        client = self.get_connection(ResourceIndex.PREFIX)  # type: ignore
        data = await client.get(guild_id)

        if not data:
            raise errors.EntryNotFound(f"Prefix entry `{guild_id}` not found")
        return json.loads(str(data))

    async def iter_prefixes(self, *, window_size: int = redis.WINDOW_SIZE) -> traits.CacheIterator[t.Sequence[str]]:
        return redis_iterators.Iterator(
            self, ResourceIndex.PREFIX, json.loads, window_size=window_size  # type: ignore
        )

    async def set_prefixes(self, guild_id: snowflakes.Snowflakeish, prefixes: t.Sequence[str], /) -> None:
        client = self.get_connection(ResourceIndex.PREFIX)  # type: ignore
        await client.set(int(guild_id), json.dumps(prefixes))


class RedisCache(redis.RedisCache, PrefixCache):
    pass
