from __future__ import annotations

import datetime

import lightbulb
import pytz

from kangakari.utils import helpers

plugin = lightbulb.Plugin("Time")


@plugin.command
@lightbulb.option("text", "The remind text.", required=False)
@lightbulb.option("timedelta", "The timedelta to remind you.")
@lightbulb.command("reminder", "Create a reminder.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_reminder(ctx: lightbulb.context.SlashContext) -> None:
    timedelta = helpers.str_to_timedelta(ctx.options.timedelta)
    if timedelta is None:
        await ctx.respond("Couldn't convert timedelta.")
        return
    text = ctx.options.text
    ctx.bot.d.scheduler.add_job(
        ctx.respond,
        "date",
        (f"{ctx.author.mention}\nReminder{f': `{text}`' if text else ''}",),
        {"user_mentions": True},
        next_run_time=datetime.datetime.now() + timedelta,
    )
    await ctx.respond("Created a reminder.")


@plugin.command
@lightbulb.option("timezone", "The timezone.", default="UTC")
@lightbulb.option("timedelta", "The timedelta.")
@lightbulb.command("time_in", "Get the time.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_time_in(ctx: lightbulb.context.SlashContext) -> None:
    timedelta = helpers.str_to_timedelta(ctx.options.timedelta)
    if timedelta is None:
        await ctx.respond("Couldn't convert timedelta.")
        return
    try:
        timezone = pytz.timezone(ctx.options.timezone)
    except pytz.UnknownTimeZoneError:
        await ctx.respond("Unknown timezone.")
        return
    unix_timestamp = int(
        (datetime.datetime.utcnow() + timedelta + timezone.utcoffset(datetime.datetime.utcnow())).timestamp()
    )
    await ctx.respond(f"It will be <t:{unix_timestamp}:f>.")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
