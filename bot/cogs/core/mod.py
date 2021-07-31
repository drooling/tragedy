# -*- coding: utf-8 -*-

import asyncio
import aiomysql
import logging
import pprint
import typing

import discord
from discord import errors
from discord.colour import Color
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import bot.utils.utilities as tragedy

class Mod(commands.Cog, description="Commands to moderate your server !"):
	def __init__(self, bot):
		self.bot = bot
		self.pool = asyncio.get_event_loop().run_until_complete(aiomysql.create_pool(
			host=tragedy.DotenvVar("mysqlServer"),
			user="root",
			password=tragedy.DotenvVar("mysqlPassword"),
			port=3306,
			db="tragedy",
			charset='utf8mb4',
			cursorclass=aiomysql.cursors.DictCursor,
			autocommit=True
		))

	@commands.command(ignore_extra=True, aliases=["changeprefix", "changepref"],
					  description="changes tragedy's prefix for this server", help="prefix <prefix>")
	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	async def prefix(self, ctx, prefix: str):
		try:
			async with self.pool.aquire() as connection:
				async with connection.cursor() as cursor:
					await cursor.execute(
						"UPDATE prefix SET prefix=%s WHERE guild=%s", (prefix, str(ctx.guild.id)))
					await self.pool.commit()
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
		await ctx.channel.purge(limit=amount)

	@purge.command(name='until')
	async def _until(self, ctx, message_id: int):
		try:
			message = await ctx.channel.fetch_message(message_id)
		except errors.NotFound:
			pass

		await ctx.message.delete()
		await ctx.channel.purge(after=message)

	@purge.command(name='user')
	async def _user(self, ctx, user: commands.UserConverter, amount: typing.Optional[int] = 100):
		def check(msg):
			return ctx.author.id == user.id
		await ctx.message.delete()
		await ctx.channel.purge(limit=amount, check=check, before=None)

	@purge.command(name="all")
	async def _all(self, ctx):
		await ctx.message.delete()
		await ctx.channel.purge(bulk=True, limit=9999999999999999999999)
		try:
			async with self.pool.aquire() as connection:
				async with connection.cursor() as cursor:
					await cursor.execute(
						"SELECT * FROM prefix WHERE guild=%s", (ctx.guild.id)
						)
					await ctx.send(embed=discord.Embed(title="Channel Nuked!",
													   description="Type \"{}help\" for commands.".format(
														   await cursor.fetchone().get('prefix')),
													   color=discord.Color.green()).set_image(
						url='https://media.giphy.com/media/HhTXt43pk1I1W/source.gif'))
		except Exception as exc:
			tragedy.logError(exc)


def setup(bot):
	bot.add_cog(Mod(bot))


while __name__ == "__main__":
	try:
		databaseConfig.ping(reconnect=False)
	except Exception as exc:
		logging.log(logging.CRITICAL, exc)
		logging.log(logging.INFO, "Attempting to reconnect to MySQL database in '{}'".format(
			__file__[:-3]))
		databaseConfig = aiomysql.connect(
			host=tragedy.DotenvVar("mysqlServer"),
			user="root",
			password=tragedy.DotenvVar("mysqlPassword"),
			port=3306,
			db="tragedy",
			charset='utf8mb4',
			cursorclass=aiomysql.cursors.DictCursor,
			autocommit=True
		)
