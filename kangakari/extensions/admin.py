from __future__ import annotations

import logging
from io import BytesIO
from subprocess import PIPE
from subprocess import run

import hikari
import lightbulb

plugin = lightbulb.Plugin("Admin")

log = logging.getLogger(__name__)


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("shutdown", "Shut the bot down.", ephemeral=True)
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_shutdown(ctx: lightbulb.context.SlashContext) -> None:
    log.info("Shutting down")
    await ctx.respond("Now shutting down.")
    await ctx.bot.close()


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("reload", "Reload all the extensions.", ephemeral=True)
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_reload(ctx: lightbulb.context.SlashContext) -> None:
    log.info("Reloading all extensions.")
    ctx.bot.reload_extensions(*ctx.bot.extensions)
    await ctx.respond("Reloaded all extensions.")


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("code", "The code to evaluate.")
@lightbulb.command("python", "Evaluate python code.", ephemeral=True)
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_python(ctx: lightbulb.context.SlashContext) -> None:
    code = ctx.options.code
    try:
        result = eval(code)
    except Exception as e:
        result = e
    await ctx.respond(f"```py\n>>> {code}\n{result}\n```")


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("cmd", "The command to evaluate.")
@lightbulb.command("shell", "Evaluate shell code.", ephemeral=True)
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_sh(ctx: lightbulb.context.SlashContext) -> None:
    cmd = ctx.options.cmd
    p = run(cmd, stdout=PIPE, stderr=PIPE)
    await ctx.respond(f"```sh\n$ {cmd}```**stdout:**```\n{p.stdout.decode()}```**stderr:**```\n{p.stderr.decode()}```")


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("id", "The ID of the error.")
@lightbulb.command("error", "Get the error message.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_error(ctx: lightbulb.context.SlashContext) -> None:
    id = ctx.options.id
    record = await ctx.bot.d.db.fetch_record("SELECT message, timestamp FROM errors WHERE error_id = $1", id)
    if record is None:
        await ctx.respond("No error with that ID.")
        return

    message, timestamp = record
    m = await ctx.respond(f"Error on <t:{int(timestamp.timestamp())}:f>")
    b = BytesIO(message.encode())
    b.seek(0)
    await m.edit(attachment=hikari.Bytes(b, f"error_{id}.txt"))

    # directly sending attachments doesn't work


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
