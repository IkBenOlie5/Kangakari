import time

import lightbulb


class Info(lightbulb.Plugin):
    @lightbulb.command(name="ping")
    async def ping_cmd(self, ctx: lightbulb.Context) -> None:
        start = time.time()
        msg = await ctx.respond_embed("uwu")
        end = time.time()

        await msg.edit(
            embed=ctx.bot.embeds.build(
                ctx=ctx,
                description=f"**Gateway**: {ctx.bot.heartbeat_latency * 1000:,.0f} ms\n**REST**: {(end - start) * 1000:,.0f} ms",
            )
        )


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Info())


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Info")
