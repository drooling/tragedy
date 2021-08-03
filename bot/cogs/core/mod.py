# -*- coding: utf-8 -*-

import asyncio
from datetime import datetime
import typing

import discord
from discord.channel import DMChannel
import pymysql
import pprint
import humanize
from discord import errors
from discord.colour import Color
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands.cooldowns import BucketType

import bot.utils.utilities as tragedy


class Mod(commands.Cog, description="Commands to moderate your server !"):
	def __init__(self, bot):
		self.bot = bot
		self.cache = {}
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

	@tasks.loop(seconds=35)
	async def mysqlPing(self):
		connected = bool(self.pool.open)
		tragedy.logInfo("Testing connection to mysql database () --> {}".format(str(connected).upper()))
		if connected is False:
			self.pool.ping(reconnect=True)
			tragedy.logInfo("Reconnecting to database () --> SUCCESS")
		else:
			pass

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		if message.author.bot is False and isinstance(message.channel, DMChannel) is not True:
			try:
				attachment = await message.attachments[0].to_file()
			except IndexError:
				attachment = None
			self.cache[message.channel.id] = [message.content, attachment, message.created_at, message.author.id]

	@commands.command()
	@commands.cooldown(1, 10, commands.BucketType.member)
	@commands.bot_has_guild_permissions(send_messages=True, embed_links=True)
	async def snipe(self, ctx):
		if not ctx.channel.id in self.cache:
			return await ctx.send('Nothing to snipe.')
		data = self.cache[ctx.channel.id]
		user = await self.bot.fetch_user(data[-1])
		time = data[2]
		embed=discord.Embed(color=Color.green())
		embed.set_author(name=user.display_name, icon_url=user.avatar_url)
		if data[0]:
			embed.description = data[0]
		if data[1]:
			if str(data[1].filename).endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
				embed.set_image(url="attachment://{}".format(data[1].filename))
				embed.set_footer(text='Sniped message sent at {}'.format(time.strftime("%I:%M %p")))
				del self.cache[ctx.channel.id]
				return await ctx.send(embed=embed, file=data[1])
		embed.set_footer(text='Sniped message sent at {}'.format(time.strftime("%I:%M %p")))
		del self.cache[ctx.channel.id]
		await ctx.send(embed=embed)

	@commands.command(ignore_extra=True, aliases=["changeprefix", "changepref"],
					  description="changes tragedy's prefix for this server", help="prefix <prefix>")
	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	async def prefix(self, ctx, prefix: str):
		try:
			with self.pool.cursor() as cursor:
				cursor.execute(
					"UPDATE prefix SET prefix=%s WHERE guild=%s", (prefix, str(ctx.guild.id)))
				self.pool.commit()
			embed = discord.Embed(title="Prefix Changed", description="New prefix - \"{}\"".format(prefix),
								  color=Color.green())
			await ctx.reply(embed=embed)
			_self = await ctx.guild.fetch_member(self.bot.user.id)
			await _self.edit(nick="[{}] tragedy".format(prefix))
		except Exception as exc:
			tragedy.logError(exc)
			embed = discord.Embed(
				title="Error", description="Failed to change prefix", color=Color.red())
			await ctx.reply(embed=embed)

	@commands.command(ignore_extra=True, description="kicks specified member from server",
					  help="kick <member> [reason]")
	@commands.guild_only()
	@commands.has_permissions(kick_members=True)
	@commands.bot_has_guild_permissions(kick_members=True)
	@commands.cooldown(1, 5, type=BucketType.member)
	async def kick(self, ctx, member: commands.MemberConverter, *, reason: str = None):
		if not reason:
			try:
				await member.kick("Kicked by {}".format(ctx.author))
				await ctx.reply(embed=discord.Embed(title="Member Kicked",
													description="{} was kicked by {} for an unspecified reason.".format(
														member, ctx.author), color=discord.Color.green()))
				try:
					await member.send(embed=discord.Embed(title="You Were Kicked",
														  description="You were kicked from {} by {} for an unspecified reason.".format(
															  ctx.message.guild.name, ctx.author),
														  color=discord.Color.green()))
				except:
					pass
				return
			except Exception as exc:
				tragedy.logError(exc)
		else:
			try:
				await member.kick(reason="Kicked by {} for \"{}\"".format(ctx.author, reason))
				await ctx.reply(embed=discord.Embed(title="Member Kicked",
													description="{} was kicked by {} for \"{}\".".format(member,
																										 ctx.author,
																										 reason),
													color=discord.Color.green()))
				try:
					await member.send(embed=discord.Embed(title="You Were Kicked",
														  description="You were kicked from {} by {} for \"{}\".".format(
															  ctx.guild.name, ctx.author, reason),
														  color=discord.Color.green()))
				except:
					pass
				return
			except Exception as exc:
				tragedy.logError(exc)

	@commands.command(ignore_extra=True, description="bans specified member from server", help="ban <member> [reason]")
	@commands.guild_only()
	@commands.has_permissions(ban_members=True)
	@commands.bot_has_guild_permissions(ban_members=True)
	@commands.cooldown(1, 5, type=BucketType.member)
	async def ban(self, ctx, member: commands.MemberConverter, *, reason: str = None):
		if not reason:
			await member.ban(reason="Banned by {}".format(ctx.author))
			embed = discord.Embed(title="You Were Banned",
								  description="You were banned from {} by {} for an unspecified reason.".format(
									  ctx.message.guild.name, ctx.author), color=discord.Color.green())
			await ctx.reply(embed=discord.Embed(title="Member Banned",
												description="{} was banned by {} for an unspecified reason.".format(
													member, ctx.author), color=discord.Color.green()))
			try:
				await member.send(embed=embed)
			except:
				pass
		else:
			await member.ban(reason="Banned by {} for \"{}\"".format(ctx.author, reason))
			await ctx.reply(embed=discord.Embed(title="Member Banned",
												description="{} was banned by {} for \"{}\".".format(member.name,
																									 ctx.author,
																									 reason),
												color=discord.Color.green()))
			try:
				await member.send(embed=discord.Embed(title="You Were Banned",
													  description="You were banned from {} by {} for \"{}\".".format(
														  ctx.guild.name, ctx.author, reason),
													  color=discord.Color.green()))
			except:
				pass

	@commands.command(description="lock's specified channel from specified role/everyone", help="lock [channel] [role]")
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	@commands.cooldown(1, 5, commands.BucketType.member)
	async def lock(self, ctx, channel: commands.TextChannelConverter = None, role: commands.RoleConverter = None):
		channel = channel or ctx.channel
		role = role or ctx.guild.default_role

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

	@commands.guild_only()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_guild_permissions(manage_messages=True)
	@commands.cooldown(1, 15, type=BucketType.member)
	@commands.group(invoke_without_command=True)
	async def purge(self, ctx, amount: int):
		await ctx.message.delete()
		await ctx.channel.purge(limit=amount + 1)
		temp = await ctx.send(">>> Purged `{}` Messages".format(amount))
		await asyncio.sleep(5)
		await temp.delete()

	@purge.command(name='until')
	async def _until(self, ctx, message_id: int):
		try:
			message = await ctx.channel.fetch_message(message_id)
		except errors.NotFound:
			pass

		await ctx.message.delete()
		await ctx.channel.purge(after=message)

	@purge.command(name='user')
	async def _user(self, ctx, user: commands.MemberConverter, amount: typing.Optional[int] = 100):
		def check(msg):
			return msg.author.id == user.id

		await ctx.channel.purge(limit=amount, check=check, before=None, bulk=True)

	@purge.command(name="all")
	async def _all(self, ctx):
		await ctx.message.delete()
		await ctx.channel.purge(bulk=True, limit=9999999999999999999999)
		try:
			with self.pool.cursor() as cursor:
				cursor.execute(
					"SELECT * FROM prefix WHERE guild=%s", (ctx.guild.id)
				)
				await ctx.send(embed=discord.Embed(title="Channel Nuked!",
												   description="Type \"{}help\" for commands.".format(
													   cursor.fetchone().get('prefix')),
												   color=discord.Color.green()).set_image(
					url='https://media.giphy.com/media/HhTXt43pk1I1W/source.gif'))
		except Exception as exc:
			tragedy.logError(exc)


def setup(bot):
	bot.add_cog(Mod(bot))
