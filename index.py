import os
import discord
from discord.ext.commands import DefaultHelpCommand
from discord.ext import commands
from prodict import Prodict
import json

from data import Bot
from models import Guild
from utils import permissions, default
import chalk

config = default.get("config.json")
description = """
A Discord Trading bot made for CG Discord Server
"""


class HelpFormat(DefaultHelpCommand):
    def get_destination(self, no_pm: bool = False):
        if no_pm:
            return self.context.channel
        else:
            return self.context.author

    async def send_error_message(self, error):
        destination = self.get_destination(no_pm=True)
        await destination.send(error)

    async def send_command_help(self, command):
        self.add_command_formatting(command)
        self.paginator.close_page()
        await self.send_pages(no_pm=True)

    async def send_pages(self, no_pm: bool = True):
        try:
            if permissions.can_react(self.context):
                await self.context.message.add_reaction(chr(0x2709))
        except discord.Forbidden:
            pass

        try:
            destination = self.get_destination(no_pm=no_pm)
            for page in self.paginator.pages:
                await destination.send(page)
        except discord.Forbidden:
            destination = self.get_destination(no_pm=True)
            await destination.send("Couldn't send help to you due to blocked DMs...")


print(chalk.cyan("Logging in..."))


async def prefixes_for(guild):
    _guild = Guild.find_one({'guild_id': str(guild.id)})
    if not _guild:
        guild_template = {
            'guild_id': str(guild.id),
            'name': guild.name,
            'prefix': config.prefix
        }
        guild_id = Guild.insert_one(guild_template).inserted_id
        _guild = Guild.find_one({'guild_id': str(guild.id)})

    return _guild.prefix


async def get_prefix(bot, message):
    extras = await prefixes_for(message.guild)
    extras = [extras]
    return commands.when_mentioned_or(*extras)(bot, message)


bot = Bot(command_prefix=get_prefix, prefix=get_prefix, command_attrs=dict(hidden=True),
          help_command=HelpFormat())

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

bot.run(config.token)
