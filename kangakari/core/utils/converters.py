import datetime
import re

import lightbulb
import pytz

TIMEDELTA_REGEX = re.compile(
    r"((?P<weeks>\d+?)w|weeks)?((?P<days>\d+?)d|days)?((?P<hours>\d+?)h|hr|hours)?"
    + r"((?P<minutes>\d+?)m|min|minutes)?((?P<seconds>\d+?)s|sec|seconds)?"
)


async def timezone_converter(arg: lightbulb.converters.WrappedArg) -> datetime.tzinfo:
    try:
        return pytz.timezone(str(arg))
    except pytz.UnknownTimeZoneError:
        raise lightbulb.errors.ConverterFailure


async def timedelta_converter(arg: lightbulb.converters.WrappedArg) -> datetime.timedelta:
    parts = TIMEDELTA_REGEX.match(str(arg))
    if parts is None:
        raise lightbulb.errors.ConverterFailure
    parts = parts.groupdict()
    return datetime.timedelta(
        weeks=float(parts["weeks"]) if parts["weeks"] else 0,
        days=float(parts["days"]) if parts["days"] else 0,
        hours=float(parts["hours"]) if parts["hours"] else 0,
        minutes=float(parts["minutes"]) if parts["minutes"] else 0,
        seconds=float(parts["seconds"]) if parts["seconds"] else 0,
    )
