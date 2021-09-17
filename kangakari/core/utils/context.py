import typing

from lightbulb import Context

if typing.TYPE_CHECKING:
    from hikari import Message


class Context(Context):
    async def info(self, embed_description: str, text: str = "", *args: typing.Any, **kwargs: typing.Any) -> "Message":
        embed = self.bot.embeds.build(
            ctx=self, title=":information_source:", description=embed_description, color=self.bot.config.INFO_COLOR
        )
        return await self.respond(text, embed=embed, *args, **kwargs)

    async def success(
        self, embed_description: str, text: str = "", *args: typing.Any, **kwargs: typing.Any
    ) -> "Message":
        embed = self.bot.embeds.build(
            ctx=self, title=":white_check_mark:", description=embed_description, color=self.bot.config.SUCCESS_COLOR
        )
        return await self.respond(text, embed=embed, *args, **kwargs)

    async def warning(
        self, embed_description: str, text: str = "", *args: typing.Any, **kwargs: typing.Any
    ) -> "Message":
        embed = self.bot.embeds.build(
            ctx=self, title=":warning:", description=embed_description, color=self.bot.config.WARNING_COLOR
        )
        return await self.respond(text, embed=embed, *args, **kwargs)

    async def error(self, embed_description: str, text: str = "", *args: typing.Any, **kwargs: typing.Any) -> "Message":
        embed = self.bot.embeds.build(
            ctx=self, title=":x:", description=embed_description, color=self.bot.config.ERROR_COLOR
        )
        return await self.respond(text, embed=embed, *args, **kwargs)
