import typing

from lightbulb import Context as Context_

if typing.TYPE_CHECKING:
    from hikari import Message

from kangakari.core import Config


class Context(Context_):
    __slots__ = ()

    async def info(self, embed_description: str, text: str = "", *args: typing.Any, **kwargs: typing.Any) -> "Message":
        embed = self.bot.embeds.build(
            ctx=self, title=":information_source:", description=embed_description, color=Config.INFO_COLOR
        )
        return await self.respond(text, embed=embed, *args, **kwargs)

    async def success(
        self, embed_description: str, text: str = "", *args: typing.Any, **kwargs: typing.Any
    ) -> "Message":
        embed = self.bot.embeds.build(
            ctx=self, title=":white_check_mark:", description=embed_description, color=Config.SUCCESS_COLOR
        )
        return await self.respond(text, embed=embed, *args, **kwargs)

    async def warning(
        self, embed_description: str, text: str = "", *args: typing.Any, **kwargs: typing.Any
    ) -> "Message":
        embed = self.bot.embeds.build(
            ctx=self, title=":warning:", description=embed_description, color=Config.WARNING_COLOR
        )
        return await self.respond(text, embed=embed, *args, **kwargs)

    async def error(self, embed_description: str, text: str = "", *args: typing.Any, **kwargs: typing.Any) -> "Message":
        embed = self.bot.embeds.build(ctx=self, title=":x:", description=embed_description, color=Config.ERROR_COLOR)
        return await self.respond(text, embed=embed, *args, **kwargs)
