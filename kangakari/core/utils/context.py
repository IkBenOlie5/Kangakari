from __future__ import annotations

import typing

from lightbulb import Context

if typing.TYPE_CHECKING:
    from hikari import Message


class Context(Context):
    async def respond_embed(self, content: str, *args: typing.Any, **kwargs: typing.Any) -> Message:
        embed = self.bot.embeds.build(ctx=self, description=content)
        return await self.respond(embed=embed, *args, **kwargs)
