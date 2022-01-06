from __future__ import annotations

import lightbulb

plugin = lightbulb.Plugin("NSFW")


@plugin.command
@lightbulb.add_checks(lightbulb.nsfw_channel_only)
@lightbulb.option("tags", "The tags to search for.")
@lightbulb.command("rule34", "Search posts on rule34.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_rule34(ctx: lightbulb.context.SlashContext) -> None:
    async with ctx.bot.d.session.get(
        "https://api.rule34.xxx/index.php",
        params={
            "page": "dapi",
            "s": "post",
            "q": "index",
            "json": 1,
            "limit": 1,
            "tags": ctx.options.tags.replace(" ", "+"),
        },
    ) as resp:
        json = await resp.json()
        if json is None:
            await ctx.respond("No post was found with those tag(s).")
            return
        post = json[0]
    await ctx.respond(post["sample_url"])


@plugin.command
@lightbulb.add_checks(lightbulb.nsfw_channel_only)
@lightbulb.option("query", "The query to search for.")
@lightbulb.command("porn", "Search a video on eporner.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_porn(ctx: lightbulb.context.SlashContext) -> None:
    async with ctx.bot.d.session.get(
        "https://www.eporner.com/api/v2/video/search/",
        params={"per_page": 1, "query": ctx.options.query.replace(" ", "+")},
    ) as resp:
        json = await resp.json()
        if json is None:
            await ctx.respond("No video was found with that query.")
            return
        video = json["videos"][0]
    await ctx.respond(video["url"])


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
