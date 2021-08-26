import datetime
import inspect
import textwrap
import time
import typing as t

import hikari
import lightbulb
from pytz import utc

from kangakari.core.utils import command_converter
from kangakari.core.utils import timedelta_converter
from kangakari.core.utils import timezone_converter


class Time(lightbulb.Plugin):
    """Time commands."""

    @lightbulb.command(name="time_in", aliases=["timein", "ti"])
    async def time_in_command(
        self, ctx: lightbulb.Context, timedelta: timedelta_converter, timezone: timezone_converter = utc
    ) -> None:
        """Get the time."""
        unix = int(
            (datetime.datetime.utcnow() + timedelta + timezone.utcoffset(datetime.datetime.utcnow())).timestamp()
        )
        await ctx.respond_embed(f"It will be <t:{unix}:f>.")

    @staticmethod
    async def send_reminder(ctx: lightbulb.Context, text: str) -> None:
        await ctx.respond(f"Reminder for: {ctx.author.mention}\n{text}")

    @lightbulb.command(name="reminder", aliases=["remind"])
    async def reminder_command(
        self, ctx: lightbulb.Context, timedelta: timedelta_converter, *, text: str = ""
    ) -> None:
        """Create a reminder to help you."""
        ctx.bot.scheduler.add_job(
            self.send_reminder,
            "date",
            (ctx, text),
            next_run_time=datetime.datetime.now() + timedelta,
        )

        await ctx.respond_embed("Created a reminder.")


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Time())


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Time")
