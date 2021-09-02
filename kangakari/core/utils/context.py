from __future__ import annotations

import typing

from lightbulb import Context

if typing.TYPE_CHECKING:
    from hikari import Message


class Context(Context):
    async def info(self, content: str, *args: typing.Any, **kwargs: typing.Any) -> Message:
        embed = self.bot.embeds.build(ctx=self, description=content, color=self.bot.config.INFO_COLOR)
        return await self.respond(embed=embed, *args, **kwargs)

    async def success(self, content: str, *args: typing.Any, **kwargs: typing.Any) -> Message:
        embed = self.bot.embeds.build(ctx=self, description=content, color=self.bot.config.SUCCESS_COLOR)
        return await self.respond(embed=embed, *args, **kwargs)

    async def warning(self, content: str, *args: typing.Any, **kwargs: typing.Any) -> Message:
        embed = self.bot.embeds.build(ctx=self, description=content, color=self.bot.config.WARNING_COLOR)
        return await self.respond(embed=embed, *args, **kwargs)

    async def error(self, content: str, *args: typing.Any, **kwargs: typing.Any) -> Message:
        embed = self.bot.embeds.build(ctx=self, description=content, color=self.bot.config.ERROR_COLOR)
        return await self.respond(embed=embed, *args, **kwargs)
