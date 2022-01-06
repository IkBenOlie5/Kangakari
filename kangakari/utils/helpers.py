import datetime
import re

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
