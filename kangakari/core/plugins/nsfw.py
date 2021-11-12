import typing

from lightbulb import Plugin
from lightbulb import checks
from lightbulb import commands

if typing.TYPE_CHECKING:
    from kangakari import Bot
    from kangakari.core import Context
from kangakari.core import Config


class NSFW(Plugin):
    """Commands that can only be run in NSFW channels."""

    __slots__ = ()

    @checks.check(checks.nsfw_channel_only)
    @commands.command(name="rule34", aliases=["r34"])
    async def rule34_command(self, ctx: "Context", *, tags: str = "") -> None:
        """Search rule34.xxx for a post."""
        async with ctx.bot.session.get(
            "https://r34-json-api.herokuapp.com/posts/", params={"limit": 1, "tags": tags.replace(" ", "+")}
        ) as resp:
            try:
                post = (await resp.json(content_type=None))[0]
            except IndexError:
                await ctx.error(f"No post was found with tag(s) `{tags}`.")
                return
        await ctx.respond(
            embed=ctx.bot.embeds.build(
                ctx=ctx,
                description=f"[Original Post]({post['file_url']})",
                image=post["file_url"],
                color=Config.SUCCESS_COLOR,
            )
        )
        # TODO: this doesn't work if the file url is for a video

    @checks.check(checks.nsfw_channel_only)
    @commands.command(name="porn", aliases=["prn"])
    async def porn_command(self, ctx: "Context", *, query: str = "") -> None:
        """Search eporner.com for a video."""
        async with ctx.bot.session.get(
            "https://www.eporner.com/api/v2/video/search/", params={"per_page": 1, "query": query.replace(" ", "+")}
        ) as resp:
            try:
                video = (await resp.json(content_type=None))["videos"][0]
            except IndexError:
                await ctx.error(f"No video was found with query `{query}`.")
        await ctx.respond(
            embed=ctx.bot.embeds.build(
                ctx=ctx,
                description=f"[Original Video]({video['url']})",
                image=video["default_thumb"]["src"],
                color=Config.SUCCESS_COLOR,
            )
        )


def load(bot: "Bot") -> None:
    bot.add_plugin(NSFW())


def unload(bot: "Bot") -> None:
    bot.remove_plugin("NSFW")
