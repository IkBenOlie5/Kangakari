import lightbulb


class NSFW(lightbulb.Plugin):
    @lightbulb.checks.nsfw_channel_only()
    @lightbulb.command(name="rule34", aliases=["r34"])
    async def rule34_command(self, ctx: lightbulb.Context, *, tags: str = "") -> None:
        async with ctx.bot.session.get(
            "https://r34-json-api.herokuapp.com/posts", params={"limit": 1, "tags": tags.replace(" ", "+")}
        ) as resp:
            try:
                post = (await resp.json(content_type=None))[0]
            except IndexError:
                return await ctx.respond_embed(f"No post was found with tag(s) `{tags}`.")
        embed = ctx.bot.embeds.build(ctx=ctx, image=post[0]["file_url"])
        await ctx.respond(embed=embed)


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(NSFW())


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("NSFW")
