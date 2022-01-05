from __future__ import annotations

import datetime
import re

import lightbulb
import pytz

plugin = lightbulb.Plugin("Time")

TIMEDELTA_REGEX = re.compile(
    r"((?P<years>\d+?)Y|years)?((?P<months>\d+?)M|months)?((?P<weeks>\d+?)W|weeks)?((?P<days>\d+?)D|days)?"
    + r"((?P<hours>\d+?)h|hr|hours)?((?P<minutes>\d+?)m|min|minutes)?((?P<seconds>\d+?)s|sec|seconds)?"
)
TIME_TO_SECONDS = {
    "years": 31_536_000,
    "months": 2_628_288,
    "weeks": 604_800,
    "days": 86_400,
    "hours": 3600,
    "minutes": 60,
    "seconds": 1,
}


def str_to_timedelta(timedelta_str: str) -> datetime.timedelta | None:
    parts = TIMEDELTA_REGEX.match(timedelta_str)
    seconds = 1.0  # to not error when your try to respond immediately
    if parts is None:
        return None
    for k, v in parts.groupdict().items():
        if v is None:
            continue
        seconds += float(v) * TIME_TO_SECONDS[k]

    return datetime.timedelta(seconds=seconds)


@plugin.command
@lightbulb.option("text", "The remind text.", required=False)
@lightbulb.option("timedelta", "The timedelta to remind you.")
@lightbulb.command("reminder", "Create a reminder.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_reminder(ctx: lightbulb.context.SlashContext) -> None:
    timedelta = str_to_timedelta(ctx.options.timedelta)
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
    timedelta = str_to_timedelta(ctx.options.timedelta)
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
