import asyncio
import logging
import discord
from discord.ext import commands
import json
import os
from dislash import *
import resources.utilities as tragedy

with open("configuration.json", "r") as config:
	data = json.load(config)
	owner_id = data["owner_id"]


token = tragedy.dotenvVar("token")

class Initiate(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self._last_member = None


bot = commands.AutoShardedBot(tragedy.custom_prefix, intents=discord.Intents.all(), owner_id=owner_id, case_insensitive=True, strip_after_prefix=True, loop=asyncio.get_event_loop() , activity=discord.Activity(name="https://linktr.ee/incriminating", type=discord.ActivityType.watching), status=discord.Status.dnd)
slash = SlashClient(bot)

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='./debug/logs.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


if __name__ == '__main__':
	os.system('clear')
	for subdir in os.listdir("Cogs"):
		for filename in os.listdir("Cogs/{}".format(subdir)):
			if filename.endswith(".py"):
				try:
					bot.load_extension("Cogs.{}.{}".format(subdir.replace('/', '.'), filename[:-3]))
				except discord.ext.commands.ExtensionError as exc:
					tragedy.logError(exc)
				except discord.ext.commands.errors.ExtensionNotLoaded as exc:
					tragedy.logError(exc)

bot.run(token)