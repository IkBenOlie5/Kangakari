import typing as t
from os import environ
from pathlib import Path

from dotenv import load_dotenv


class Config:
    __slots__: t.Sequence[str] = ()
    _cache: t.Dict[str, t.Any] = {}
    _types: t.Dict[str, t.Callable[[str], t.Any]] = {
        "bool": bool,
        "int": int,
        "float": float,
        "file": lambda x: Path(x).read_text().strip("\n"),
        "str": str,
        "list": lambda x: [Config.resolve_value(y) for y in x.split(",")],
    }

    def __init__(self) -> None:
        load_dotenv()

    @staticmethod
    def resolve_value(string: str) -> t.Any:
        type_, value = ("str", string) if ":" not in string else string.split(":", maxsplit=1)
        return Config._types.get(type_, str)(value)

    def _get(self, key: str) -> t.Any:
        if (cached := self._cache.get(key)) is not None:
            return cached
        value: t.Optional[str] = environ.get(key)
        if value is None:
            raise ValueError(f"Key {key} not in environment variables.")
        self._cache[key] = value
        return self.resolve_value(value)

    def __getattr__(self, key: str) -> t.Any:
        return self._get(key)

    def __getitem__(self, key: str) -> t.Any:
        return self._get(key)
