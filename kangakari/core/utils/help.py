import typing as t

import lightbulb


class Help(lightbulb.help.HelpCommand):
    async def object_not_found(self, ctx: lightbulb.Context, name: str) -> None:
        await ctx.respond_embed(f"`{name}` is not a valid plugin, command or group.")

    @staticmethod
    async def check_runnable(ctx: lightbulb.Context, cmd: t.Union[lightbulb.Command, lightbulb.Group]) -> bool:
        try:
            await cmd.is_runnable(ctx)
            return True
        except lightbulb.errors.CheckFailure:
            return False

    async def send_help_overview(self, ctx: lightbulb.Context) -> None:
        plugin_commands = [
            [plugin.name, await lightbulb.help.filter_commands(ctx, plugin._commands.values())]
            for plugin in self.bot.plugins.values()
        ]
        all_plugin_commands = []
        for _, commands in plugin_commands:
            all_plugin_commands.extend(commands)
        uncategorised_commands = await lightbulb.help.filter_commands(
            ctx, self.bot.commands.difference(set(all_plugin_commands))
        )
        plugin_commands.insert(0, ["Uncategorised", uncategorised_commands])

        help_text = ["> __**Bot help**__\n"]
        for plugin, commands in plugin_commands:
            if not commands:
                continue
            help_text.append(f"> **{plugin}**")
            for c in sorted(commands, key=lambda c: c.name):
                short_help = lightbulb.help.get_help_text(c).split("\n")[0]
                help_text.append(f"• `{c.name}` - {short_help}")
        help_text.append(f"\n> Use `{ctx.clean_prefix}help [command]` for more information.")
        await ctx.respond_embed("\n".join(help_text))

    async def send_plugin_help(self, ctx: lightbulb.Context, plugin: lightbulb.Plugin) -> None:
        await ctx.respond_embed(
            f"> **Help for plugin `{plugin.name}`**\n"
            + (lightbulb.help.get_help_text(plugin).replace("\n", "\n> ") or "No help text provided.")
            + "\n\nCommands:"
            + "\n```\n"
            + (
                "\n".join(f"{c.name}" for c in sorted(plugin._commands.values(), key=lambda c: c.name))
                or "No commands in the plugin."
            )
            + "```"
        )

    async def send_command_help(self, ctx: lightbulb.Context, cmd: lightbulb.Command) -> None:
        await ctx.respond_embed(
            f"> **Help for command `{cmd.name}`**\n"
            + (lightbulb.help.get_help_text(cmd) or "No help text provided.")
            + "\n\nUsage:"
            + f"\n```{ctx.clean_prefix}{lightbulb.help.get_command_signature(cmd)}```"
            + f"\nRunnable by you? `{'yes' if await self.check_runnable(ctx, cmd) else 'no'}`"
        )

    async def send_group_help(self, ctx: lightbulb.Context, group: lightbulb.Group) -> None:
        await ctx.respond_embed(
            f"> **Help for command group `{group.name}`**\n"
            + (lightbulb.help.get_help_text(group) or "No help text provided.")
            + "\n\nUsage:"
            + f"```{ctx.clean_prefix}{lightbulb.help.get_command_signature(group)}```"
            + (
                (
                    "\nSubcommands:"
                    + "\n```\n"
                    + "\n".join(c.name for c in sorted(group.subcommands, key=lambda c: c.name))
                    + "```"
                )
                if group.subcommands
                else "No subcommands in the group."
            )
            + f"\nRunnable by you? `{'yes' if await self.check_runnable(ctx, group) else 'no'}`"
        )
