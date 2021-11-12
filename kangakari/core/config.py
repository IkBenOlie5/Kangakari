import typing
from os import environ
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class ConfigMeta(type):
    def resolve_value(cls, value: str):
        _map: typing.Dict[str, typing.Callable[[str], typing.Any]] = {
            "bool": bool,
            "int": int,
            "float": float,
            "file": lambda x: Path(x).read_text().strip("\n"),
            "str": str,
            "list": lambda x: [Config.resolve_value(y) for y in x.split(",")],
        }

        return _map[(v := value.split(":", maxsplit=1))[0]](v[1])

    def __getattr__(cls, name):
        return cls.resolve_value(environ[name])


class Config(metaclass=ConfigMeta):
    pass
