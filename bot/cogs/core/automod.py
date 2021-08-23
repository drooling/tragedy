# -*- coding: utf-8 -*-

import discord
import re
import aiohttp
import contextlib

from discord.colour import Color
from discord.ext import commands
from discord.permissions import Permissions

class Automod(commands.Cog, command_attrs=dict(hidden=True)):
	def __init__(self, bot):
		self.bot = bot
		self.aiohttp = aiohttp.ClientSession()
		self.domains: list = ["top.gg/", "discord.gg/", ".gg/", "discord.io/", "dsc.gg/"]
		self.AutoModTypesNONE = dict(linkFilter=False, mentionFilter=False, mentionLength=0, spamFilter=False, spamRatio=(0, 0))
		self.AutoModTypesLOW = dict(linkFilter=False, mentionFilter=True, mentionLength=8, spamFilter=True, spamRatio=(5, 3))
		self.AutoModTypesMEDIUM = dict(linkFilter=True, mentionFilter=True, mentionLength=6, spamFilter=True, spamRatio=(5, 3))
		self.AutoModTypesHIGH = dict(linkFilter=True,  mentionFilter=True, mentionLength=3, spamFilter=True, spamRatio=(5, 3))

	@commands.Cog.listener()
	async def on_message(self, message: discord.Message):
		with contextlib.suppress(Exception):
			if message.guild.id == 769727903419990037:
				if bool(re.findall(discord.utils._URL_REGEX, message.clean_content)):
					await self.rickroll_filter(message)
				if bool(message.raw_mentions):
					await self.mention_filter(message, 3)
	
	async def link_filter(self, message: discord.Message):
		if any(domain in str(message.content).lower() for domain in self.domains):
			await message.delete()
			await message.channel.send(embed=discord.Embed(
				title="Tragedy Auto-mod",
				description="Invite links are not allowed in this server",
				color=Color.red()
			))
		else:
			return

	async def mention_filter(self, message: discord.Message, max_mentions: int):
		if len(message.raw_mentions) >= max_mentions:
			if not message.author.guild_permissions.administrator:
				await message.delete()
				await message.channel.send(embed=discord.Embed(
					title="Tragedy Auto-mod",
					description="You cannot mention more than %s members at a time" % (str(max_mentions)),
					color=Color.red()
				))
			else:
				return
		else:
			return

	async def rickroll_filter(self, message: discord.Message):
		rick_emojis = ['\U0001F1F7', '\U0001F1EE', '\U0001F1E8', '\U0001F1F0']
		phrases = ["rickroll", "rick roll", "rick astley", "never gonna give you up"]
		source = str(await (await self.aiohttp.get(re.findall(pattern=discord.utils._URL_REGEX, string=message.content, flags=re.MULTILINE | re.IGNORECASE)[0], allow_redirects=True)).content.read()).lower()
		rickRoll = bool((re.findall('|'.join(phrases), source, re.MULTILINE | re.IGNORECASE)))
		if rickRoll:
			[await message.add_reaction(emoji) for emoji in rick_emojis]
		else:
			return

def setup(bot):
	bot.add_cog(Automod(bot))