import re
import typing
from datetime import timedelta

if typing.TYPE_CHECKING:
    from lightbulb import WrappedArg
    from lightbulb import Command
    from datetime import tzinfo

from lightbulb.errors import ConverterFailure
from pytz import UnknownTimeZoneError
from pytz import timezone

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


async def timezone_converter(arg: "WrappedArg") -> "tzinfo":
    try:
        return timezone(arg.data)
    except UnknownTimeZoneError:
        raise ConverterFailure


async def timedelta_converter(arg: "WrappedArg") -> timedelta:
    parts = TIMEDELTA_REGEX.match(arg.data)
    if parts is None:
        raise ConverterFailure

    seconds = 0.0
    for k, v in parts.groupdict().items():
        if v is None:
            continue
        seconds += float(v) * TIME_TO_SECONDS[k]

    return timedelta(seconds=seconds)


async def command_converter(arg: "WrappedArg") -> "Command":
    command = arg.context.bot.get_command(arg.data)
    if command is None:
        raise ConverterFailure

    return command
