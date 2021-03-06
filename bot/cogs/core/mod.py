# -*- coding: utf-8 -*-

import asyncio
import collections
import contextlib
from datetime import datetime, timezone
import pprint
import random
import string
import typing
import time

from discord.embeds import Embed
from bot.utils.paginator import Paginator

import bot.utils.utilities as tragedy
import bot.utils.classes as classes
import discord
import humanize
import nanoid
import pymysql.cursors
from bot.utils.classes import WelcomeNotConfigured
from discord.channel import DMChannel
from discord.colour import Color
from discord.ext import commands, tasks
from discord.ext.commands.converter import TextChannelConverter
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.errors import BadArgument
from discord.permissions import Permissions
from discord_components import *
from discord_components.component import Button, ButtonStyle


class Mod(commands.Cog, description="Commands to moderate your server !"):
	def __init__(self, bot):
		self.bot = bot
		self.snipe_cache = collections.defaultdict(dict)
		self.edit_cache = collections.defaultdict(dict)
		self.pool = pymysql.connect(host=tragedy.DotenvVar("mysqlServer"), user="root", password=tragedy.DotenvVar("mysqlPassword"), port=3306, database="tragedy", charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, read_timeout=5, write_timeout=5, connect_timeout=5, autocommit=True)
		self.mysqlPing.start()
		DiscordComponents(self.bot)

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

	async def get_roles(self, guild: discord.Guild):
		with self.pool.cursor() as cursor:
			cursor.execute("SELECT role FROM `auto-role` WHERE guild=%s", (guild.id))
		rows = cursor.fetchall()
		try:
			return [guild.get_role(dict.get("role")) for dict in rows]
		except (KeyError, AttributeError):
			return None

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		roles = await self.get_roles(member.guild)
		if roles != None:
			with contextlib.suppress(Exception):
				await member.add_roles(*roles, reason="tragedy Auto-Role")
		else:
			return

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		with self.pool.cursor() as cursor:
			cursor.execute(
				"SELECT channel, message FROM `welcome` WHERE guild=%s", (member.guild.id))
			row: dict = cursor.fetchone()
			try:
				channelID = row.get("channel")
				message = row.get("message")
			except AttributeError:
				return
			try:
				channel = await self.bot.fetch_channel(channelID)
				await channel.send(self.ConvertMessage(member, message))
			except:
				return

	def ConvertMessage(self, member: discord.Member, message: str):
		variables = {
			"user": member,
			"user_ping": member.mention,
			"user_name": member.name,
			"server_name": member.guild.name,
			"join_position": sum(m.joined_at < member.joined_at for m in member.guild.members if m.joined_at is not None)
		}

		template: str = string.Template(str(message))
		formatted = template.safe_substitute(**variables)
		return formatted

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		if message.author.bot is False and isinstance(message.channel, DMChannel) is not True:
			self.snipe_cache[message.channel.id] = message

	@commands.Cog.listener()
	async def on_message_edit(self, before: discord.Message, after: discord.Message):
		if after.author.bot is False and isinstance(after.channel, DMChannel) is not True:
			self.edit_cache[after.channel.id] = {
				"before": before, "after": after
			}

	@commands.command()
	@commands.guild_only()
	@commands.cooldown(1, 10, commands.BucketType.member)
	@commands.bot_has_guild_permissions(send_messages=True, embed_links=True)
	async def snipe(self, ctx):
		if not ctx.channel.id in self.snipe_cache:
			return await ctx.send('Nothing to snipe.')
		data: discord.Message = self.snipe_cache[ctx.channel.id]
		time = data.created_at
		embed = discord.Embed(color=Color.green(), timestamp=time)
		embed.set_author(name=data.author.display_name,
						 icon_url=data.author.display_avatar.url)
		if data.content:
			embed.description = data.content
		if data.attachments:
			if str(data.attachments[0].filename).lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
				embed.set_image(
					url="attachment://{}".format(data.attachments[0].filename))
				embed.set_footer(text='Sniped message sent at {}'.format(
					time.strftime("%I:%M %p")))
				del self.snipe_cache[ctx.channel.id]
				return await ctx.send(embed=embed, file=await data.attachments[0].to_file())
		del self.snipe_cache[ctx.channel.id]
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	@commands.cooldown(1, 10, commands.BucketType.member)
	@commands.bot_has_guild_permissions(send_messages=True, embed_links=True)
	async def editsnipe(self, ctx):
		if not ctx.channel.id in self.edit_cache:
			return await ctx.send('Nothing to snipe.')

		before: discord.Message = self.edit_cache[ctx.channel.id]["before"]
		after: discord.Message = self.edit_cache[ctx.channel.id]["after"]
		edited_at = after.created_at

		embed = discord.Embed(color=Color.green(), timestamp=edited_at)
		embed.set_author(name=after.author,
						 url=after.jump_url,
						 icon_url=after.author.display_avatar.url)
		if after.content:
			embed.add_field(
				name="Before", value=before.clean_content, inline=False)
			embed.add_field(
				name="After", value=after.clean_content, inline=False)
		del self.edit_cache[ctx.channel.id]
		await ctx.send(embed=embed)

	@commands.command(ignore_extra=True, description="kicks specified member from server",
					  help="kick <member> [reason]")
	@commands.guild_only()
	@commands.has_permissions(kick_members=True)
	@commands.bot_has_guild_permissions(kick_members=True)
	@commands.cooldown(1, 5, type=BucketType.member)
	async def kick(self, ctx, members: commands.Greedy[classes.MemberConverter], *, reason: typing.Optional[str]):
		reason = reason or "an unspecified reason"
		success: list = list()
		failure: list = list()
		for member in members:
			try:
				await member.kick(reason=reason + " - " + str(ctx.author))
				with contextlib.suppress(Exception):
					await member.send(embed=discord.Embed(title="You have been kicked", color=discord.Color.red(), description="You have been kicked from `{}` for `{}` as of <t:{}:f>".format(ctx.guild.name, reason, int(time.time()))))
				success.append(member)
			except discord.Forbidden:
				failure.append(member)
		embed = discord.Embed(title="Kick", color=Color.green() if len(success) > len(failure) else Color.red())
		embed.add_field(name="Successfully Kicked", value='\n'.join([str(member) for member in success]) or "None")
		embed.add_field(name="Failed to Kick", value='\n'.join([str(member) for member in failure]) or "None")
		await ctx.reply(mention_author=True, embed=embed)

	@commands.command(ignore_extra=True, description="bans specified member from server", help="ban <member(s)> [reason]")
	@commands.guild_only()
	@commands.has_permissions(ban_members=True)
	@commands.bot_has_guild_permissions(ban_members=True)
	@commands.cooldown(1, 5, type=BucketType.member)
	async def ban(self, ctx, members: commands.Greedy[classes.MemberConverter], *, reason: typing.Optional[str]):
		reason = reason or "an unspecified reason"
		success: list = list()
		failure: list = list()
		for member in members:
			try:
				await member.ban(reason=reason + " - " + str(ctx.author))
				with contextlib.suppress(Exception):
					await member.send(embed=discord.Embed(title="You have been banned", color=discord.Color.red(), description="You have been banned from `{}` for `{}` as of <t:{}:f> by `{}`".format(ctx.guild.name, reason, int(time.time()), ctx.author)))
				success.append(member)
			except discord.Forbidden:
				failure.append(member)
		embed = discord.Embed(title="Ban", color=Color.green() if len(success) > len(failure) else Color.red())
		embed.add_field(name="Successfully Banned", value='\n'.join([str(member) for member in success]) or "None")
		embed.add_field(name="Failed to Ban", value='\n'.join([str(member) for member in failure]) or "None")
		await ctx.reply(mention_author=True, embed=embed)

	@commands.command(description="lock's specified channel from specified role/everyone", help="lock [channel] [role]")
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	@commands.cooldown(1, 5, commands.BucketType.member)
	async def lock(self, ctx, channel: commands.TextChannelConverter = None, role: commands.RoleConverter = None):
		channel = channel or ctx.channel
		role = role or ctx.guild.default_role
		try:
			if ctx.guild.default_role not in channel.overwrites:
				overwrites = {
					role: discord.PermissionOverwrite(send_messages=False)
				}
				await channel.edit(overwrites=overwrites)
				embed = discord.Embed(description='{} has been locked :lock:.'.format(
					channel.mention), color=Color.green())
				await ctx.send(embed=embed)
			elif channel.overwrites[role].send_messages or channel.overwrites[role].send_messages is None:
				overwrites = channel.overwrites[role]
				overwrites.send_messages = False
				await channel.set_permissions(role, overwrite=overwrites)
				embed = discord.Embed(description='{} has been locked. :lock:'.format(
					channel.mention), color=Color.green())
				await ctx.send(embed=embed)
			else:
				overwrites = channel.overwrites[role]
				overwrites.send_messages = True
				await channel.set_permissions(role, overwrite=overwrites)
				embed = discord.Embed(description='{} has been unlocked. :unlock:'.format(channel.mention),
									  color=Color.green())
				await ctx.send(embed=embed)
		except discord.Forbidden:
			embed = discord.Embed(title="Oops !",
								  description="I cannot do that that you silly goose.",
								  color=discord.Color.red())
			await ctx.reply(embed=embed, mention_author=True)

	@commands.command()
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	@commands.cooldown(1, 5, commands.BucketType.member)
	async def lockdown(self, ctx: commands.Context, role: commands.RoleConverter = None):
		for channel in ctx.guild.text_channels:
			role = role or ctx.guild.default_role
			try:
				if ctx.guild.default_role not in channel.overwrites:
					overwrites = {
						role: discord.PermissionOverwrite(send_messages=False)
					}
					await channel.edit(overwrites=overwrites)
				elif channel.overwrites[role].send_messages or channel.overwrites[role].send_messages is None:
					overwrites = channel.overwrites[role]
					overwrites.send_messages = False
					await channel.set_permissions(role, overwrite=overwrites)
			except discord.Forbidden:
				embed = discord.Embed(title="Oops !",
									  description="I cannot do that that you silly goose.",
									  color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
		embed = discord.Embed(description='Server has been put on lockdown. :lock:'.format(
						channel.mention), color=Color.green())

	@commands.command(description="`warn` will warn specified user", help="warn <member> [reason]")
	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 15, BucketType.guild)
	async def warn(self, ctx: commands.Context, member: commands.MemberConverter, *, reason: str = None):
		reason = "None Specified." if reason is None else reason
		if member.bot is True or member.top_role >= ctx.author.top_role:
			return await ctx.send("You cannot do that.")
		try:
			with self.pool.cursor() as cursor:
				cursor.execute("INSERT INTO warns (id, guild, user, warner, reason) VALUES (%s, %s, %s, %s, %s)", (
					nanoid.generate(size=10), ctx.guild.id, member.id, ctx.author.id, reason))
			await ctx.send("**{}** has been warned.".format(member.mention))
		except Exception as exc:
			tragedy.logError(exc)

	@commands.command(name='warns', description="Views specified user's warnings in this server", help="warns <member>")
	@commands.guild_only()
	@commands.cooldown(1, 15, BucketType.guild)
	async def _warns(self, ctx, *, member: commands.MemberConverter):
		def check(response):
			return ctx.author == response.user and response.channel == ctx.channel
		try:
			embed = discord.Embed(color=Color.green()).set_author(
				icon_url=member.display_avatar.url, name=member)
			warns = list()
			ids = list()
			with self.pool.cursor() as cursor:
				cursor.execute(
					"SELECT * FROM warns WHERE guild=%s AND user=%s", (ctx.guild.id, member.id))
				rows = cursor.fetchall()
			if not rows:
				embed.description = "No warnings."
				return await ctx.reply(embed=embed, mention_author=True)
			else:
				for _row in rows:
					tragedy_warning_id = _row.get("id")
					warner = _row.get("warner")
					reason = _row.get("reason")
					time = humanize.naturaldate(_row.get("time"))
					ids.append(tragedy_warning_id)
					warns.append(str("**ID** - `{}` | **Admin** - <@{}> | **Date** - `{}` | **Reason** - `{}`".format(
						tragedy_warning_id, warner, time, reason)))
				index = 1
				for _warning in warns:
					embed.add_field(name="Warning {}.".format(
						index), value=_warning, inline=False)
					index += 1

				Confirm = await ctx.reply(embed=embed, mention_author=True, components=[
					[
						Button(style=ButtonStyle.green,
							   label="Clear warnings"),
						Button(style=ButtonStyle.green,
							   label="Remove a warning"),
						Button(style=ButtonStyle.red, label="X")
					]
				])

				try:
					try:
						interaction = await self.bot.wait_for("button_click", check=check, timeout=15)
					except asyncio.exceptions.TimeoutError:
						await Confirm.edit(embed=embed, components=[])
					if interaction.component.label == "X":
						await Confirm.edit(embed=embed, components=[])
						await ctx.message.delete()
						await Confirm.delete()
					elif interaction.component.label == "Clear warnings" and Permissions.manage_guild in ctx.author.guild_permissions:
						await Confirm.edit(embed=embed, components=[])
						await ctx.message.delete()
						await Confirm.delete()
						with self.pool.cursor() as cursor:
							cursor.execute(
								"DELETE FROM warns WHERE guild=%s AND user=%s", (ctx.guild.id, member.id))
						await ctx.send("Cleared all of {}'s warnings.".format(member.mention), delete_after=5)
					elif interaction.component.label == "Remove a warning" and Permissions.manage_guild in ctx.author.guild_permissions:
						await Confirm.edit(embed=embed, components=[])
						SelectOptions = []
						for _id in ids:
							SelectOptions.append(
								SelectOption(label=_id, value=_id))
						SelectWarn = await ctx.send(components=[
							[
								Select(
									placeholder="Select the ID you wish to delete.",
									max_values=1,
									options=SelectOptions
								)
							]
						])
						try:
							selectInteraction = await self.bot.wait_for("select_option", check=check, timeout=45)
						except asyncio.exceptions.TimeoutError:
							return await SelectWarn.edit(content="Took too long !", embed=None, components=[])
						await ctx.message.delete()
						await SelectWarn.delete()
						with self.pool.cursor() as cursor:
							cursor.execute("DELETE FROM warns WHERE guild=%s AND user=%s AND id=%s", (
								ctx.guild.id, member.id, selectInteraction.component[0].label))
						await ctx.send("Removed warning from {}\nID - **{}**".format(member.mention, selectInteraction.component[0].label), delete_after=5)
				except Exception as exc:
					tragedy.logError(exc)
		except Exception as exc:
			tragedy.logError(exc)

	@commands.group(ignore_extra=True, invoke_without_command=True, description="`prefix` will show this server's prefix(es)", help="prefix")
	@commands.guild_only()
	@commands.cooldown(1, 15, BucketType.guild)
	async def prefix(self, ctx: commands.Context):
		try:
			prefixes = tragedy.getServerPrefixes(ctx.guild.id)
			numberedList = list()
			for index, value in enumerate(prefixes, 1):
				if value == "xv ":
					numberedList.append(
						"{}. `{}` (Default Prefix)".format(index, value))
				else:
					numberedList.append("{}. `{}`".format(index, value))
			embed = discord.Embed(title="Prefixes", description='\n'.join(numberedList),
								  color=Color.green())
			embed.set_footer(
				text="{}/5 Custom Prefixes".format(len(prefixes) - 1))
			await ctx.reply(embed=embed)
		except Exception as exc:
			tragedy.logError(exc)

	@prefix.command(name='add', description="Adds new prefix to tragedy's prefix(es) for this server", help="prefix add <prefix>")
	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 60, BucketType.guild)
	async def _add(self, ctx, *, prefix: str):
		try:
			prefixes = tragedy.getServerPrefixes(ctx.guild.id)
			if prefix in prefixes:
				return await ctx.send("That's already one of my prefixes !", delete_after=5)
			if (len(prefixes) - 1) > 4:
				return await ctx.send("You have set too many prefixes (maximum of 5). Remove one to continue adding more !", delete_after=5)
			if len(prefix) > 10:
				return await ctx.send("That's too long for our database ! Try to keep it below 10 characters.", delete_after=5)
			with self.pool.cursor() as cursor:
				cursor.execute(
					"SELECT * FROM prefix WHERE guild=%s", (str(ctx.guild.id)))
				response = cursor.fetchone()
				try:
					column = list(response.keys())[
						list(response.values()).index(None)]
				except AttributeError:
					column = "prefix1"
			with self.pool.cursor() as cursor:
				cursor.execute(
					"UPDATE prefix SET {0}=%s WHERE guild=%s".format(
						column), (prefix, str(ctx.guild.id))
				)
			embed = discord.Embed(title="Prefix Added", description='Added `%s` to my prefixes for this server !' % (prefix),
								  color=Color.green())
			await ctx.reply(embed=embed)
		except Exception as exc:
			tragedy.logError(exc)

	@prefix.command(name='remove', description="Removes prefix from tragedy's prefix(es) for this server", help="prefix remove <prefix>")
	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	@commands.cooldown(1, 60, BucketType.guild)
	async def _remove(self, ctx, *, prefix: str):
		try:
			if prefix in list(["xv ", "xv"]):
				return await ctx.send("You cannot remove default prefix.", delete_after=5)
			prefixes = tragedy.getServerPrefixes(ctx.guild.id)
			if prefix not in prefixes:
				return await ctx.send("That is not currently a prefix for this server.", delete_after=5)
			if (len(prefixes) - 1) < 1:
				return await ctx.send("You have to keep at least 1 prefix.", delete_after=5)
			with self.pool.cursor() as cursor:
				cursor.execute(
					"SELECT * FROM prefix WHERE guild=%s", (str(ctx.guild.id)))
				response = dict(cursor.fetchone())
				column = list(response.keys())[
					list(response.values()).index(prefix)]
				cursor.execute("UPDATE prefix SET {0}=NULL WHERE guild=%s".format(
					column), (str(ctx.guild.id)))
			embed = discord.Embed(title="Prefix Removed", description='Removed `%s` from my prefixes for this server !' % (prefix),
								  color=Color.green())
			await ctx.reply(embed=embed)
		except Exception as exc:
			tragedy.logError(exc)

	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	@commands.group(ignore_extra=True, invoke_without_command=True, description="Auto-welcome commands", help="welcome")
	async def welcome(self, ctx):
		with self.pool.cursor() as cursor:
			cursor.execute(
				"SELECT channel, message FROM `welcome` WHERE guild=%s", (ctx.guild.id))
			row: dict = cursor.fetchone()
			try:
				channel = row.get("channel")
				message = row.get("message")
			except AttributeError:
				raise WelcomeNotConfigured("Welcome has not been configured")
			channel = await self.bot.fetch_channel(channel)
			embed = discord.Embed(title="Auto-welcome", description="Your auto-welcome is configured to use %s with the message\n```%s```" %
								  (channel.mention, message), color=Color.green())
			await ctx.send(embed=embed)

	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	@welcome.group(ignore_extra=True, invoke_without_command=True)
	async def setup(self, ctx: commands.Context):
		with self.pool.cursor() as cursor:
			cursor.execute("INSERT INTO `welcome` (guild) VALUES (%s)", (ctx.guild.id))

	@welcome.command()
	async def test(self, ctx):
		with self.pool.cursor() as cursor:
			cursor.execute(
				"SELECT channel, message FROM `welcome` WHERE guild=%s", (ctx.guild.id))
			row: dict = cursor.fetchone()
			try:
				channel = row.get("channel")
				message = row.get("message")
			except AttributeError:
				raise WelcomeNotConfigured("Welcome has not been configured")
			channel = await self.bot.fetch_channel(channel)
			await channel.send(self.ConvertMessage(ctx.author, message))

	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	@welcome.group(ignore_extra=True, invoke_without_command=True, description="Set Auto-welcome variables", help="welcome set <variable>")
	@commands.cooldown(1, 45, BucketType.guild)
	async def set(self, ctx):
		embed = discord.Embed(
			title="Auto-welcome Configuration",
			description="Use the following commands to configure auto-welcome for this server",
			color=Color.green()
		)
		embed.add_field(name="welcome set channel",
						value="Sets the channel to send the welcome messages in", inline=False)
		embed.add_field(name="welcome set message",
						value="Sets the welcome message", inline=False)
		await ctx.send(embed=embed)

	@set.command()
	@commands.cooldown(1, 35, BucketType.guild)
	async def channel(self, ctx, channel: TextChannelConverter):
		with self.pool.cursor() as cursor:
			cursor.execute("UPDATE `welcome` SET channel=%s WHERE guild=%s", (str(
				channel.id), str(ctx.guild.id)))
		await ctx.send(embed=discord.Embed(
			title="Auto-welcome Configuration",
			description="Welcome channel set to `#%s`" % (channel.name),
			color=Color.green()
		))

	@set.command()
	@commands.cooldown(1, 35, BucketType.guild)
	async def message(self, ctx, *, message: typing.Optional[str]):
		if not message:
			embed = discord.Embed(
				title="Auto-welcome Configuration",
				description="You can use the following variables in your welcome message",
				color=Color.green()
			)
			embed.add_field(name="${user}", value="Example: Welcome ${user} ! (Welcome %s !)" % (
				ctx.author), inline=False)
			embed.add_field(name="${user_ping}", value="Example: Welcome ${user_ping} ! (Welcome %s !)" % (
				ctx.author.mention), inline=False)
			embed.add_field(name="${user_name}", value="Example: Welcome ${user_name} ! (Welcome %s !)" % (
				ctx.author.name), inline=False)
			embed.add_field(name="${server_name}", value="Example: Welcome to ${server_name} ! (Welcome to %s !)" % (
				ctx.guild.name), inline=False)
			embed.add_field(name="${join_postion}", value="Example: You are the ${join_position}th person to join ! (Welcome to %s !)" % (
				sum(m.joined_at < ctx.author.joined_at for m in ctx.guild.members if m.joined_at is not None)), inline=False)
			return await ctx.send(embed=embed)
		if len(message) > 1849:
			raise BadArgument("Message cannot be over 1850 characters.")
		else:
			with self.pool.cursor() as cursor:
				cursor.execute("UPDATE `welcome` SET message=%s WHERE guild=%s", (str(
					message), str(ctx.guild.id)))
			await ctx.send(embed=discord.Embed(
				title="Auto-welcome Configuration",
				description="Welcome message set.",
				color=Color.green()
			))

	@commands.guild_only()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_guild_permissions(manage_messages=True)
	@commands.cooldown(1, 15, type=BucketType.member)
	@commands.group(invoke_without_command=True)
	async def purge(self, ctx, amount: typing.Optional[int] = 5):
		await ctx.message.delete()
		await ctx.channel.purge(limit=amount)
		temp = await ctx.send(">>> Purged `{}` Messages".format(amount))
		await asyncio.sleep(5)
		await temp.delete()

	@purge.command(name='until')
	async def _until(self, ctx, message: commands.MessageConverter):
		await ctx.message.delete()
		await ctx.channel.purge(after=message)

	@purge.command(name='user')
	async def _user(self, ctx, user: commands.MemberConverter, amount: typing.Optional[int] = 100):
		def check(msg):
			return msg.author.id == user.id

		await ctx.channel.purge(limit=amount, check=check, before=None, bulk=True)

	@purge.command(name="all")
	async def _all(self, ctx: commands.Context):
		def check(response):
			return ctx.author == response.user and response.channel == ctx.channel

		Confirm = await ctx.reply(embed=discord.Embed(title="Are you sure?", description="This will delete **every message** in this channel.", color=Color.red()), mention_author=True, components=[
			[
				Button(style=ButtonStyle.green, label="Yes"),
				Button(style=ButtonStyle.red, label="No")
			]
		])

		try:
			interaction = await self.bot.wait_for("button_click", check=check, timeout=15)
			if interaction.component.label == "Yes":
				try:
					await Confirm.delete()
					position_index = ctx.channel.position
					await ctx.channel.delete()
					clone = await ctx.channel.clone()
					await clone.edit(position=position_index)
					try:
						await clone.send(embed=discord.Embed(title="Channel Nuked!",
														   description="Type \"{}help\" for commands.".format(
															   random.choice(tragedy.getServerPrefixes(ctx.guild.id))),
														   color=discord.Color.green()).set_image(
							url='https://media.giphy.com/media/HhTXt43pk1I1W/source.gif'), delete_after=5)
					except Exception as exc:
						tragedy.logError(exc)
				except discord.Forbidden:
					raise commands.BotMissingPermissions(["manage_channels"])
			else:
				await Confirm.delete()
				await ctx.message.delete()
				return
		except asyncio.exceptions.TimeoutError:
			await Confirm.edit(content="Took too long !", embed=None, components=[])

	@commands.command()
	@commands.has_permissions(manage_emojis=True)
	async def steal(self, ctx: commands.Context, emoji: commands.EmojiConverter):
		emoji: discord.Emoji = emoji
		await ctx.guild.create_custom_emoji(name=emoji.name, reason="tragedy Emoji Steal", image=await emoji.url.read())
		await ctx.send(embed=discord.Embed(
			title="Emoji Steal",
			color=Color.green(),
			description="{} added with name `:{}:`".format(emoji, emoji.name)
		))

	@commands.group(ignore_extra=True, invoke_without_command=True)
	@commands.has_permissions(manage_guild=True)
	async def autorole(self, ctx: commands.Context):
		await ctx.send(embed=discord.Embed(title="tragedy Auto-Role", color=Color.green(), description='\n'.join(role.mention for role in await self.get_roles(ctx.guild)) or "No Auto-Roles"))

	@autorole.command()
	@commands.has_permissions(manage_guild=True)
	async def add(self, ctx: commands.Context, role: commands.RoleConverter):
		roles = await self.get_roles(ctx.guild)
		if role in roles:
			return await ctx.reply("That role is already configured as an auto-role.", delete_after=5)
		with self.pool.cursor() as cursor:
			cursor.execute("INSERT INTO `auto-role` (guild, role) VALUES (%s, %s)", (ctx.guild.id, role.id))
		await ctx.reply(embed=discord.Embed(
			title="tragedy Auto-Role",
			color=Color.green(),
			description="{} will automatically be given to users upon joining.".format(role.mention)
		))

	@autorole.command()
	@commands.has_permissions(manage_guild=True)
	async def remove(self, ctx: commands.Context, role: commands.RoleConverter):
		roles = await self.get_roles(ctx.guild)
		if role not in roles:
			return await ctx.reply("That role is not configured as an auto-role.", delete_after=5)
		with self.pool.cursor() as cursor:
			cursor.execute("DELETE FROM `auto-role` WHERE guild=%s AND role=%s", (ctx.guild.id, role.id))
		await ctx.reply(embed=discord.Embed(
			title="tragedy Auto-Role",
			color=Color.green(),
			description="`{}` Removed from Auto-Role".format(role.name)
		))

	@commands.command()
	async def sus(self, ctx: commands.Context):
		sus: list = list(collections.defaultdict())
		embeds: list = list()

		async def filter(member: discord.Member):
			if member.bot:
				return
			if not member.avatar:
				avatar = True
			else:
				avatar = False
			if (member.created_at.date() - datetime.today().date()).days > 30:
				return sus.append({"nigga": (member, avatar)})
			else:
				return

		for member in ctx.guild.members:
			await filter(member)

		index = 0
		for _ in range(round(len(sus) / 4)):
			embed = discord.Embed(title="Suspicious Members", color=Color.green())
			for local in range(4):
				embed.add_field(name=sus[index + local].get("nigga")[0], value="Account created <t:{}:R>. Default Avatar - **{}**".format(int(sus[index + local].get("nigga")[0].created_at.timestamp()), str(sus[index + local].get("nigga")[1])), inline=False)
			index += 4
			embeds.append(embed)

		await Paginator(self.bot, ctx, embeds, timeout=30).run()


def setup(bot):
	bot.add_cog(Mod(bot))