import asyncio
import logging
import discord
from discord.ext import commands
import os
from dislash import *
import bot.resources.utilities as tragedy
import sys

token = tragedy.dotenvVar("token")

class Initiate(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self._last_member = None


bot = commands.AutoShardedBot(tragedy.custom_prefix, intents=discord.Intents.all(), case_insensitive=True, strip_after_prefix=True, loop=asyncio.get_event_loop() , activity=discord.Activity(name="https://linktr.ee/incriminating", type=discord.ActivityType.watching), status=discord.Status.dnd)
slash = SlashClient(bot)

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


if __name__ == '__main__':
	os.system('clear')
	for subdir in os.listdir("cogs"):
		for filename in os.listdir("cogs/{}".format(subdir)):
			if filename.endswith(".py"):
				try:
					bot.load_extension("cogs.{}.{}".format(subdir.replace('/', '.'), filename[:-3]))
				except discord.ext.commands.ExtensionError as exc:
					tragedy.logError(exc)
				except discord.ext.commands.errors.ExtensionNotLoaded as exc:
					tragedy.logError(exc)

bot.run(token)