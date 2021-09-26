import typing

from lightbulb import CommandErrorEvent
from lightbulb import Plugin
from lightbulb import errors
from lightbulb import listener

if typing.TYPE_CHECKING:
    from kangakari import Bot


class Handler(Plugin):
    """Error handler."""

    @listener(event_type=CommandErrorEvent)
    async def on_command_error(self, e: CommandErrorEvent) -> None:
        if isinstance(e.exception, (errors.CommandNotFound)):
            pass
        elif isinstance(e.exception, errors.NSFWChannelOnly):
            text = f"The command `{e.command.qualified_name}` can only be used inside a NSFW channel."
            await e.context.error(text)
        elif isinstance(e.exception, errors.NotEnoughArguments):
            text = "".join(
                [
                    f"The command `{e.command.qualified_name}` misses the argument(s): ",
                    f"`{' | '.join(e.exception.missing_args)}`.",
                ],
            )
            await e.context.error(text)
        elif isinstance(e.exception, errors.ConverterFailure):
            argument = e.exception.text.split(" ")[-1]
            text = f"Converter failed for argument: `{argument}`."
            await e.context.error(text)
        else:
            await e.context.error("I have errored, and I cannot get up.")
            raise e.exception


def load(bot: "Bot") -> None:
    bot.add_plugin(Handler())


def unload(bot: "Bot") -> None:
    bot.remove_plugin("Handler")
