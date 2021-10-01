import typing
from operator import attrgetter

from lightbulb import help
from lightbulb.errors import CheckFailure

if typing.TYPE_CHECKING:
    from lightbulb import Command
    from lightbulb import Group
    from lightbulb import Plugin

    from kangakari.core import Context


class Help(help.HelpCommand):
    __slots__ = ()

    async def object_not_found(self, ctx: "Context", name: str) -> None:
        await ctx.warning(f"`{name}` is not a valid plugin, command or group.")

    @staticmethod
    async def check_runnable(ctx: "Context", cmd: typing.Union["Command", "Group"]) -> bool:
        try:
            await cmd.is_runnable(ctx)
            return True
        except CheckFailure:
            return False

    async def send_help_overview(self, ctx: "Context") -> None:
        plugin_commands = [
            [plugin.name, await help.filter_commands(ctx, plugin._commands.values())]
            for plugin in self.bot.plugins.values()
        ]
        all_plugin_commands = []
        for _, commands in plugin_commands:
            all_plugin_commands.extend(commands)
        uncategorised_commands = await help.filter_commands(ctx, self.bot.commands.difference(set(all_plugin_commands)))
        plugin_commands.insert(0, ["Uncategorised", uncategorised_commands])

        help_text = ["> __**Bot help**__\n"]
        for plugin, commands in plugin_commands:
            if not commands:
                continue
            help_text.append(f"> **{plugin}**")
            for c in sorted(commands, key=attrgetter("name")):
                short_help = help.get_help_text(c).split("\n")[0]
                help_text.append(f"• `{c.name}` - {short_help}")
        help_text.append(f"\n> Use `{ctx.clean_prefix}help [command]` for more information.")
        await ctx.info("\n".join(help_text))

    async def send_plugin_help(self, ctx: "Context", plugin: "Plugin") -> None:
        await ctx.info(
            "\n".join(
                [
                    f"> **Help for plugin `{plugin.name}`**",
                    (help.get_help_text(plugin).replace("\n", "\n> ") or "No help text provided."),
                    "\nCommands:",
                    "```",
                    (
                        "\n".join(f"{c.name}" for c in sorted(plugin._commands.values(), key=attrgetter("name")))
                        or "No commands in the plugin."
                    ),
                    "```",
                ]
            )
        )

    async def send_command_help(self, ctx: "Context", cmd: "Command") -> None:
        await ctx.info(
            "\n".join(
                [
                    f"> **Help for command `{cmd.name}`**",
                    (help.get_help_text(cmd) or "No help text provided."),
                    "\nUsage:",
                    f"```{ctx.clean_prefix}{help.get_command_signature(cmd)}```",
                    f"Runnable by you? `{await self.check_runnable(ctx, cmd)}`",
                ]
            ),
        )

    async def send_group_help(self, ctx: "Context", group: "Group") -> None:
        await ctx.info(
            "\n".join(
                [
                    f"> **Help for command group `{group.name}`**",
                    (help.get_help_text(group) or "No help text provided."),
                    "\nUsage:",
                    f"```{ctx.clean_prefix}{help.get_command_signature(group)}```",
                    (
                        (
                            "\n".join(
                                [
                                    "\nSubcommands:",
                                    "```",
                                    "\n".join(c.name for c in sorted(group.subcommands, key=attrgetter("name"))),
                                    "```",
                                ]
                            )
                        )
                        if group.subcommands
                        else "No subcommands in the group."
                    ),
                    f"\nRunnable by you? `{await self.check_runnable(ctx, group)}`",
                ]
            )
        )
