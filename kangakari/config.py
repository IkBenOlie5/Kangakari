from __future__ import annotations

import typing as t
from functools import lru_cache
from os import environ
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class ConfigMeta(type):
    def resolve_value(cls, value: str) -> t.Any:
        _map: dict[str, t.Callable[[str], t.Any]] = {
            "bool": bool,
            "int": int,
            "float": float,
            "file": lambda x: Path(x).read_text().strip("\n"),
            "str": str,
            "list": lambda x: [cls.resolve_value(y) for y in x.split(",")],
        }

        return _map[(v := value.split(":", maxsplit=1))[0]](v[1])

    @lru_cache()
    def __getattr__(cls, name: str) -> t.Any:
        return cls.resolve_value(environ[name])


class Config(metaclass=ConfigMeta):
    pass
