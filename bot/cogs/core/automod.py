# -*- coding: utf-8 -*-

import contextlib
import datetime
import pprint
import re
import typing

import aiohttp
import bot.utils.utilities as tragedy
import discord
import pymysql.cursors
from bot.utils.classes import AutoModConfig
from discord.colour import Color
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType, CooldownMapping


class Automod(commands.Cog, description="Automatic Moderation"):
	def __init__(self, bot):
		self.bot = bot
		self._URL_REGEX = r'(?P<url><[^: >]+:\/[^ >]+>|(?:https?|steam):\/\/[^\s<]+[^<.,:;\"\'\]\s])'
		self.aiohttp = aiohttp.ClientSession(headers={"User-Agent": "tragedy", "X-Tragedy-Task": "Auto-Moderation"})
		self.domains: list = ["top.gg/", "discord.gg/", ".gg/", "discord.io/", "dsc.gg/"]
		self.pool = pymysql.connect(
			host=tragedy.DotenvVar("mysqlServer"),
			user="root",
			password=tragedy.DotenvVar("mysqlPassword"),
			port=3306,
			database="tragedy",
			charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor,
			read_timeout=5,
			write_timeout=5,
			connect_timeout=5,
			autocommit=True
		)
		self.mysqlPing.start()
		self.clear_counter.start()
		self.spam_count = {}
		self.config_cache = {}
		self.map: CooldownMapping = commands.CooldownMapping.from_cooldown(5, 2, commands.BucketType.member)
		self.AutoModTypesNONE = AutoModConfig(profanity_filter=False, invite_filter=False, mention_filter=False, mention_length=0, spam_filter=False)
		self.AutoModTypesLOW = AutoModConfig(profanity_filter=False, invite_filter=False, mention_filter=True, mention_length=8, spam_filter=True)
		self.AutoModTypesMEDIUM = AutoModConfig(profanity_filter=True, invite_filter=True, mention_filter=True, mention_length=6, spam_filter=True)
		self.AutoModTypesHIGH = AutoModConfig(profanity_filter=True, invite_filter=True,  mention_filter=True, mention_length=3, spam_filter=True)

	def convert_to_bool(self, int: int) -> bool:
		return (False if int == 0 else True)

	async def get_config(self, ctx: commands.Context) -> AutoModConfig:
		with self.pool.cursor() as cursor:
			cursor: pymysql.cursors.Cursor = cursor
			try:
				cursor.execute(
					"SELECT * FROM `auto-mod` WHERE guild=%s", (ctx.guild.id))
				row: dict = cursor.fetchone()
				return AutoModConfig(
					self.convert_to_bool(row.get("profanity_filter")),
					self.convert_to_bool(row.get("link_filter")),
					self.convert_to_bool(row.get("mention_filter")),
					row.get("mention_length"),
					self.convert_to_bool(row.get("spam_filter"))
				)
			except AttributeError:
				cursor.execute("INSERT INTO `auto-mod` (guild) VALUES (%s)", (ctx.guild.id))
				cursor.execute(
					"SELECT * FROM `auto-mod` WHERE guild=%s", (ctx.guild.id))
				row: dict = cursor.fetchone()
				return AutoModConfig(
					self.convert_to_bool(row.get("profanity_filter")),
					self.convert_to_bool(row.get("link_filter")),
					self.convert_to_bool(row.get("mention_filter")),
					row.get("mention_length"),
					self.convert_to_bool(row.get("spam_filter"))
				)

	@tasks.loop(seconds=35)
	async def mysqlPing(self):
		connected = bool(self.pool.open)
		pprint.pprint(
			"Testing connection to mysql database () --> {} IN {}".format(str(connected).upper(), __file__))
		if connected is False:
			self.pool.ping(reconnect=True)
			pprint.pprint("Reconnecting to database () --> SUCCESS")
		else:
			pass

	@tasks.loop(minutes=5)
	async def clear_counter(self):
		self.spam_count.clear()

	@commands.Cog.listener()
	async def on_message(self, message: discord.Message):
		with contextlib.suppress(Exception):
			if message.author.bot:
				return
			if not message.guild.id in self.config_cache:
				config = await self.get_config(await self.bot.get_context(message))
				self.config_cache[message.guild.id] = config
			else:
				config = self.config_cache[message.guild.id]
			config: AutoModConfig = config
			if bool(config.spam_filter):
				await self.spam_filter(message)
			if bool(config.invite_filter):
				await self.invite_filter(message)
				if bool(re.findall(self._URL_REGEX, message.clean_content)):
					await self.rickroll_filter(message)
			if bool(config.mention_filter):
				if bool(message.raw_mentions):
					await self.mention_filter(message, config.mention_length)
			if bool(config.profanity_filter):
				await self.profanity_filter(message)

	async def spam_filter(self, message: discord.Message):
		def check(payload):
			return payload.author.id == message.author.id

		if message.author.guild_permissions.administrator:
			return

		bucket = self.map.get_bucket(message)
		now = message.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()
		bucket_full = bucket.update_rate_limit(now)
		if bucket_full:
			try:
				self.spam_count[message.author.id] += 1
			except KeyError:
				self.spam_count[message.author.id] = 0
				self.spam_count[message.author.id] += 1
			if self.spam_count[message.author.id] >= 3:
				del self.spam_count[message.author.id]
				await message.author.ban(reason="Tragedy Auto-Mod | User invoked rate limit 3+ times in 5 minutes")
				return await message.channel.send(embed=discord.Embed(
					title="Tragedy Auto-Mod",
					color=Color.red(),
					description="User has been banned for repeated spamming."
				))
			await message.channel.purge(limit=5, check=check, bulk=True)
			embed = discord.Embed(title="Tragedy Auto-Mod", color=Color.red(), description="Woah Woah ! Slow down bud no spamming.")
			return await message.channel.send(content="||%s||" % (message.author.mention), embed=embed)

	async def invite_filter(self, message: discord.Message):
		if message.author.guild_permissions.administrator:
			return
		if any(domain in str(message.content).lower() for domain in self.domains):
			await message.delete()

	async def mention_filter(self, message: discord.Message, max_mentions: int):
		if len(message.raw_mentions) >= max_mentions:
			if not message.author.guild_permissions.administrator:
				await message.delete()

	async def rickroll_filter(self, message: discord.Message):
		rick_emojis = ['\U0001F1F7', '\U0001F1EE', '\U0001F1E8', '\U0001F1F0']
		phrases = ["rickroll", "rick roll", "rick astley", "never gonna give you up"]
		source = str(await (await self.aiohttp.get(re.findall(pattern=self._URL_REGEX, string=message.content, flags=re.MULTILINE | re.IGNORECASE)[0], allow_redirects=True)).content.read()).lower()
		rickRoll = bool(
			(re.findall('|'.join(phrases), source, re.MULTILINE | re.IGNORECASE)))
		if rickRoll:
			[await message.add_reaction(emoji) for emoji in rick_emojis]

	async def profanity_filter(self, message: discord.Message):
		content: str = message.clean_content
		if message.author.guild_permissions.administrator:
			return
		clean: bool = bool(self.profanity.is_clean(content))
		if not clean:
			await message.delete()

	@commands.group(ignore_extra=True, invoke_without_command=True)
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 45, BucketType.guild)
	async def automod(self, ctx):
		await ctx.send(embed=discord.Embed(
			title="Tragedy Auto-Mod",
			color=Color.green(),
			description=str(await self.get_config(ctx))
		))

	@automod.group(ignore_extra=True, invoke_without_command=True)
	@commands.has_permissions(manage_guild=True)
	async def set(self, ctx):
		await ctx.send(embed=discord.Embed(
			title="Tragedy Auto-Mod",
			color=Color.green(),
			description="`invite` - 0/1 (0 - Disable | 1 - Enable)\n`profanity` - 0/1 (0 - Disable | 1 - Enable)\n`spam` - 0/1 (0 - Disable | 1 - Enable)\n`mention` - 0/1 (0 - Disable | 1 - Enable)\n`mention max` - Number above 3"
		))

	@set.command()
	@commands.has_permissions(manage_guild=True)
	async def invite(self, ctx, state: int):
		if state not in (0, 1):
			return await ctx.send(embed=discord.Embed(
				title="Tragedy Auto-Mod",
				color=Color.red(),
				description=":x: The Options are 0/1 (0 - Disable | 1 - Enable) !"
			))
		with self.pool.cursor() as cursor:
			cursor.execute("UPDATE `auto-mod` SET invite_filter=%s WHERE guild=%s", (state, str(ctx.guild.id)))
		del self.config_cache[ctx.guild.id]
		await ctx.send(embed=discord.Embed(
				title="Tragedy Auto-Mod",
				color=Color.green(),
				description="Invite filter state updated."
			))

	@set.command()
	@commands.has_permissions(manage_guild=True)
	async def profanity(self, ctx, state: int):
		if state not in (0, 1):
			return await ctx.send(embed=discord.Embed(
				title="Tragedy Auto-Mod",
				color=Color.red(),
				description=":x: The Options are 0/1 (0 - Disable | 1 - Enable) !"
			))
		with self.pool.cursor() as cursor:
			cursor.execute("UPDATE `auto-mod` SET profanity_filter=%s WHERE guild=%s", (state, str(ctx.guild.id)))
		del self.config_cache[ctx.guild.id]
		await ctx.send(embed=discord.Embed(
				title="Tragedy Auto-Mod",
				color=Color.green(),
				description="Profanity filter state updated."
			))

	@set.command()
	@commands.has_permissions(manage_guild=True)
	async def spam(self, ctx, state: int):
		if state not in (0, 1):
			return await ctx.send(embed=discord.Embed(
				title="Tragedy Auto-Mod",
				color=Color.red(),
				description=":x: The Options are 0/1 (0 - Disable | 1 - Enable) !"
			))
		with self.pool.cursor() as cursor:
			cursor.execute("UPDATE `auto-mod` SET spam_filter=%s WHERE guild=%s", (state, str(ctx.guild.id)))
		del self.config_cache[ctx.guild.id]
		await ctx.send(embed=discord.Embed(
				title="Tragedy Auto-Mod",
				color=Color.green(),
				description="Spam filter state updated."
			))

	@set.group(ignore_extra=True, invoke_without_command=True)
	@commands.has_permissions(manage_guild=True)
	async def mention(self, ctx, state: int):
		if state not in (0, 1):
			return await ctx.send(embed=discord.Embed(
				title="Tragedy Auto-Mod",
				color=Color.red(),
				description=":x: The Options are 0/1 (0 - Disable | 1 - Enable) !"
			))
		with self.pool.cursor() as cursor:
			cursor.execute("UPDATE `auto-mod` SET mention_filter=%s WHERE guild=%s", (state, str(ctx.guild.id)))
		del self.config_cache[ctx.guild.id]
		await ctx.send(embed=discord.Embed(
				title="Tragedy Auto-Mod",
				color=Color.green(),
				description="Mention filter state updated."
			))

	@mention.command()
	@commands.has_permissions(manage_guild=True)
	async def max(self, ctx, max: int):
		if max < 3:
			return await ctx.send(embed=discord.Embed(
				title="Tragedy Auto-Mod",
				color=Color.red(),
				description=":x: The max must be above 3 !"
			))
		with self.pool.cursor() as cursor:
			cursor.execute("UPDATE `auto-mod` SET mention_length=%s WHERE guild=%s", (max, str(ctx.guild.id)))
		del self.config_cache[ctx.guild.id]
		await ctx.send(embed=discord.Embed(
				title="Tragedy Auto-Mod",
				color=Color.green(),
				description="Mention max state updated."
			))

def setup(bot):
	bot.add_cog(Automod(bot))
