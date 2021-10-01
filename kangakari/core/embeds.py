import typing

from hikari import Color
from hikari import Embed

if typing.TYPE_CHECKING:
    from kangakari.core import Context

from datetime import datetime


class Embeds:
    __slots__ = (
        "_ctx",
        "fields",
        "title",
        "desc",
        "footer",
        "author",
        "author_icon",
        "thumbnail",
        "image",
        "color",
        "time",
    )

    def build(self, ctx: "Context", **kwargs: typing.Any) -> Embed:
        self._ctx: Context = ctx
        self.fields: typing.Optional[typing.Sequence[typing.Tuple[str, str, bool]]] = kwargs.get("fields")
        self.title: typing.Optional[str] = kwargs.get("title")
        self.desc: typing.Optional[str] = kwargs.get("description")
        self.footer: typing.Optional[str] = kwargs.get("footer")
        self.author: typing.Optional[str] = kwargs.get("author")
        self.author_icon: typing.Any = kwargs.get("author_icon")
        self.thumbnail: typing.Any = kwargs.get("thumbnail")
        self.image: typing.Any = kwargs.get("image")
        self.color: typing.Any = kwargs.get("color")
        self.time: datetime = datetime.now().astimezone()

        self.prime()
        self.plus_fields()
        self.extras()

        return self.embed

    def prime(self) -> None:
        self.embed = Embed(
            title=self.title,
            description=self.desc,
            timestamp=self.time,
            color=self.color or Color.from_hex_code(self._ctx.bot.config.EMBED_COLOR),
        )

    def plus_fields(self) -> None:
        if self.fields:
            for name, value, inline in self.fields:
                self.embed.add_field(name=name, value=value, inline=inline)

    def extras(self) -> None:
        self.embed.set_thumbnail(self.thumbnail)

        self.embed.set_author(name=self.author or "Kangakari", icon=self.author_icon)

        self.embed.set_footer(
            text=self.footer or f"Invoked by: {self._ctx.author.username}",
            icon=self._ctx.author.avatar_url or self._ctx.bot.get_me().avatar_url,
        )

        self.embed.set_image(self.image)
