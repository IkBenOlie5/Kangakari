import typing as t

import hikari
import lightbulb


class Context(lightbulb.Context):
    async def respond_embed(self, content: str, *args: t.Any, **kwargs: t.Any) -> hikari.Message:
        embed = self.bot.embeds.build(ctx=self, description=content)
        return await super().respond(embed=embed, *args, **kwargs)
