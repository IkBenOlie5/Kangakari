import lightbulb


class Handler(lightbulb.Plugin):
    @lightbulb.listener(event_type=lightbulb.CommandErrorEvent)
    async def on_command_error(self, event: lightbulb.CommandErrorEvent) -> None:
        if isinstance(event.exception, (lightbulb.errors.CommandNotFound)):
            pass
        elif isinstance(event.exception, lightbulb.errors.NSFWChannelOnly):
            text = f"The command `{event.command.qualified_name}` can only be used inside a NSFW channel."
            await event.context.respond_embed(text)
        elif isinstance(event.exception, lightbulb.errors.NotEnoughArguments):
            text = f"The command `{event.command.qualified_name}` misses the argument(s) `{' | '.join(event.exception.missing_args)}`."
            await event.context.respond_embed(text)
        else:
            await event.context.respond_embed("I have errored, and I cannot get up.")
            raise event.exception


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Handler())


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Handler")
