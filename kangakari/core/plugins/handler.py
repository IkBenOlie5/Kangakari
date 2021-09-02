from __future__ import annotations

import typing

from lightbulb import CommandErrorEvent
from lightbulb import Plugin
from lightbulb import errors
from lightbulb import listener

if typing.TYPE_CHECKING:
    from lightbulb import Bot


class Handler(Plugin):
    """Error handler."""

    @listener(event_type=CommandErrorEvent)
    async def on_command_error(self, event: CommandErrorEvent) -> None:
        if isinstance(event.exception, (errors.CommandNotFound)):
            pass
        elif isinstance(event.exception, errors.NSFWChannelOnly):
            text = f"The command `{event.command.qualified_name}` can only be used inside a NSFW channel."
            await event.context.error(text)
        elif isinstance(event.exception, errors.NotEnoughArguments):
            text = "".join(
                [
                    f"The command `{event.command.qualified_name}` misses the argument(s): ",
                    f"`{' | '.join(event.exception.missing_args)}`.",
                ],
            )
            await event.context.error(text)
        elif isinstance(event.exception, errors.ConverterFailure):
            argument = event.exception.text.split(" ")[-1]
            text = f"Converter failed for argument: `{argument}`."
            await event.context.error(text)
        else:
            await event.context.error("I have errored, and I cannot get up.")
            raise event.exception


def load(bot: Bot) -> None:
    bot.add_plugin(Handler())


def unload(bot: Bot) -> None:
    bot.remove_plugin("Handler")
