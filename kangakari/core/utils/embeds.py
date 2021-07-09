import datetime
import typing as t

import hikari
import lightbulb


class Embeds:
    def build(self, ctx, **kwargs: t.Any) -> hikari.Embed:
        self._ctx: lightbulb.Context = ctx
        self.fields: t.Optional[list[tuple[str, str, bool]]] = kwargs.get("fields")
        self.title: t.Optional[str] = kwargs.get("title")
        self.desc: t.Optional[str] = kwargs.get("description")
        self.footer: t.Optional[str] = kwargs.get("footer")
        self.author: t.Optional[str] = kwargs.get("author")
        self.author_icon: t.Any = kwargs.get("author_icon")
        self.thumbnail: t.Any = kwargs.get("thumbnail")
        self.image: t.Any = kwargs.get("image")
        self.color: t.Any = kwargs.get("color")
        self.time: datetime.datetime = datetime.datetime.now().astimezone()

        self.prime()
        self.plus_fields()
        self.extras()

        return self.embed

    def prime(self) -> None:
        self.embed = hikari.Embed(
            title=self.title,
            description=self.desc,
            timestamp=self.time,
            color=self.color or hikari.Color.from_hex_code(self._ctx.bot.config.EMBED_COLOR),
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
            icon=self._ctx.author.avatar_url or self._ctx.bot.me.avatar_url,
        )

        self.embed.set_image(self.image)
