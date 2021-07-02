import typing as t
from os import environ
from pathlib import Path

from dotenv import load_dotenv


class Config:
    __slots__: t.Sequence[str] = ()

    def __init__(self) -> None:
        load_dotenv()

    def resolve_value(self, string: str) -> t.Any:
        types: t.Dict[str, t.Callable[[str], t.Any]] = {
            "bool": bool,
            "int": int,
            "float": float,
            "file": lambda x: Path(x).read_text().strip("\n"),
            "str": str,
            "list": lambda x: [self.resolve_value(y) for y in x.split(",")],
        }
        type_, value = ("str", string) if ":" not in string else string.split(":", maxsplit=1)
        return types.get(type_, str)(value)

    def _get(self, key: str) -> t.Any:
        value: t.Optional[str] = environ.get(key)
        if value is None:
            raise ValueError(f"Key {key} not in environment variables.")
        return self.resolve_value(value)

    def __getattr__(self, key: str) -> t.Any:
        return self._get(key)

    def __getitem__(self, key: str) -> t.Any:
        return self._get(key)
