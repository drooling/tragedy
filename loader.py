import asyncio
import logging
import os
import sys

import discord
from discord.ext import commands

import bot.utils.utilities as tragedy

token = tragedy.DotenvVar("token")

bot = commands.AutoShardedBot(tragedy.custom_prefix, intents=discord.Intents.all(), case_insensitive=True,
                              strip_after_prefix=True, loop=asyncio.get_event_loop(),
                              status=discord.Status.dnd, owner_id=875513626805555232)


logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(
	'%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

if __name__ == '__main__':
	os.system('clear')
	for subdir in os.listdir("bot/cogs"):
		for filename in os.listdir("bot/cogs/{}".format(subdir)):
			if filename.endswith(".py"):
				try:
					#if filename[:-3] not in ("sms"):
					bot.load_extension("bot.cogs.{}.{}".format(
						subdir.replace('/', '.'), filename[:-3]))
				except Exception as e:
					tragedy.logError(e)

bot.run(token)
