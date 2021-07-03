import lightbulb


class Context(lightbulb.Context):
    async def respond_embed(self, content, *args, **kwargs):
        embed = self.bot.embeds.build(ctx=self, description=content)
        return await super().respond(embed=embed, *args, **kwargs)
