from lightbulb import help


class Help(help.HelpCommand):
    async def object_not_found(self, ctx, name):
        await ctx.respond_embed(f"`{name}` is not a valid plugin, command or group.")

    async def send_help_overview(self, ctx):
        plugin_commands = [
            [plugin.name, await help.filter_commands(ctx, plugin._commands.values())]
            for plugin in self.bot.plugins.values()
        ]
        all_plugin_commands = []
        for _, cmds in plugin_commands:
            all_plugin_commands.extend(cmds)
        uncategorised_commands = await help.filter_commands(
            ctx, self.bot.commands.difference(set(all_plugin_commands))
        )
        plugin_commands.insert(0, ["Uncategorised", uncategorised_commands])

        help_text = ["> __**Bot help**__\n"]
        for plugin, commands in plugin_commands:
            if not commands:
                continue
            help_text.append(f"> **{plugin}**")
            for c in sorted(commands, key=lambda c: c.name):
                short_help = help.get_help_text(c).split("\n")[0]
                help_text.append(f"• `{c.name}` - {short_help}")
        help_text.append(f"\n> Use `{ctx.clean_prefix}help [command]` for more information.")
        await ctx.respond_embed("\n".join(help_text))

    async def send_plugin_help(self, ctx, plugin):
        help_text = [
            f"> **Help for category `{plugin.name}`**",
            help.get_help_text(plugin).replace("\n", "\n> ") or "No help text provided.",
            "\nCommands:",
            ", ".join(f"`{c.name}`" for c in sorted(plugin._commands.values(), key=lambda c: c.name))
            or "No commands in the category",
        ]
        await ctx.respond_embed("\n".join(help_text))

    async def send_command_help(self, ctx, cmd):
        help_text = [
            f"> **Help for command `{cmd.name}`**",
            "\nUsage:",
            f"```{ctx.clean_prefix}{help.get_command_signature(cmd)}```",
            help.get_help_text(cmd).replace("\n", "\n> ") or "No help text provided.",
        ]
        await ctx.respond_embed("\n".join(help_text))

    async def send_group_help(self, ctx, group):
        help_text = [
            f"> **Help for command group `{group.name}`**",
            "\nUsage:",
            f"```{ctx.clean_prefix}{help.get_command_signature(group)}```",
            help.get_help_text(group).replace("\n", "\n> ") or "No help text provided.",
            f"Subcommands: {', '.join(f'`{c.name}`' for c in sorted(group.subcommands, key=lambda c: c.name))}"
            if group.subcommands
            else "No subcommands in the group",
        ]
        await ctx.respond_embed("\n".join(help_text))
