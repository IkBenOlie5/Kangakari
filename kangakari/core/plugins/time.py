import datetime

from lightbulb import Bot
from lightbulb import Context
from lightbulb import Plugin
from lightbulb import commands
from pytz import utc

from kangakari.core.utils import timedelta_converter
from kangakari.core.utils import timezone_converter


class Time(Plugin):
    """Time commands."""

    @commands.command(name="time_in", aliases=["timein", "ti"])
    async def time_in_command(
        self, ctx: Context, timedelta: timedelta_converter, timezone: timezone_converter = utc
    ) -> None:
        """Get the time."""
        unix = int(
            (datetime.datetime.utcnow() + timedelta + timezone.utcoffset(datetime.datetime.utcnow())).timestamp()
        )
        await ctx.info(f"It will be <t:{unix}:f>.")

    @staticmethod
    async def send_reminder(ctx: Context, text: str) -> None:
        await ctx.info(f"Reminder for: {ctx.author.mention}\n{text}")

    @commands.command(name="reminder", aliases=["remind"])
    async def reminder_command(self, ctx: Context, timedelta: timedelta_converter, *, text: str = "") -> None:
        """Create a reminder to help you."""
        ctx.bot.scheduler.add_job(
            self.send_reminder,
            "date",
            (ctx, text),
            next_run_time=datetime.datetime.now() + timedelta,
        )

        await ctx.success("Created a reminder.")


def load(bot: Bot) -> None:
    bot.add_plugin(Time())


def unload(bot: Bot) -> None:
    bot.remove_plugin("Time")
