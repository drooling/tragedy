# -*- coding: utf-8 -*-

import asyncio
import io
import logging
from discord.colour import Color
from discord.ext import commands
import discord
from discord.ext.commands.cooldowns import BucketType
import pymysql.cursors
import bot.utils.utilities as tragedy

databaseConfig = pymysql.connect(
	host=tragedy.dotenvVar("mysqlServer"),
	user="root",
	password=tragedy.dotenvVar("mysqlPassword"),
	port=3306,
	database="tragedy",
	charset='utf8mb4',
	cursorclass=pymysql.cursors.DictCursor,
	read_timeout=5,
	write_timeout=5,
	connect_timeout=5,
	autocommit=True
	)

cursor = databaseConfig.cursor()

class Mod(commands.Cog, description="Commands to moderate your server !"):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(ignore_extra=True, aliases=["changeprefix", "changepref"], description="chenges tragedy's prefix for this server", help="prefix <prefix>")
	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	async def prefix(self, ctx, prefix: str):
		try:
			cursor.execute("UPDATE prefix SET prefix=%s WHERE guild=%s", (prefix, str(ctx.guild.id)))
			databaseConfig.commit()
			embed = discord.Embed(title="Prefix Changed", description="New prefix - \"{}\"".format(prefix), color=Color.green())
			await ctx.reply(embed=embed)
			_self = await ctx.guild.fetch_member(self.bot.user.id)
			await _self.edit(nick="[{}] tragedy".format(prefix))
		except Exception as exc:
			tragedy.logError(exc)
			embed = discord.Embed(title="Error", description="Failed to change prefix", color=Color.red())
			await ctx.reply(embed=embed)

	@commands.command(ignore_extra=True, description="kicks specified member from server", help="kick <member> [reason]")
	@commands.guild_only()
	@commands.has_permissions(kick_members=True)
	@commands.bot_has_guild_permissions(kick_members=True)
	@commands.cooldown(1, 5, type=BucketType.member)
	async def kick(self, ctx, member: discord.Member, *, reason: str = None):
		if not reason:
			try:
				await member.kick("Kicked by {}".format(ctx.author))
				await ctx.reply(embed=discord.Embed(title="Member Kicked", description="{} was kicked by {} for an unspecified reason.".format(member, ctx.author), color=discord.Color.green()))
				try:
					await member.send(embed=discord.Embed(title="You Were Kicked", description="You were kicked from {} by {} for an unspecified reason.".format(ctx.message.guild.name, ctx.author), color=discord.Color.green()))
				except:
					pass
				return
			except Exception as exc:
				tragedy.logError(exc)
		else:
			try:
				await member.kick(reason="Kicked by {} for \"{}\"".format(ctx.author, reason))
				await ctx.reply(embed=discord.Embed(title="Member Kicked", description="{} was kicked by {} for \"{}\".".format(member, ctx.author, reason), color=discord.Color.green()))
				try:
					await member.send(embed=discord.Embed(title="You Were Kicked", description="You were kicked from {} by {} for \"{}\".".format(ctx.guild.name, ctx.author, reason), color=discord.Color.green()))
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
	async def ban(self, ctx, member: discord.Member, *, reason: str):
		memberName = member
		if not reason:
			try:
				await member.ban("Banned by {}".format(ctx.author))
				embed = discord.Embed(title="You Were Banned", description="You were banned from {} by {} for an unspecified reason.".format(ctx.message.guild.name, ctx.author), color=discord.Color.green())
				await ctx.reply(embed=discord.Embed(title="Member Banned", description="{} was banned by {} for an unspecified reason.".format(member, ctx.author), color=discord.Color.green()))
				try:
					await member.send(embed=embed)
				except:
					pass
			except:
				await ctx.reply(embed=discord.Embed(title="Error", description="Unable to ban member", color=discord.Color.red()))
		else:
			try:
				await member.ban(reason="Banned by {} for \"{}\"".format(ctx.author, reason))
				await ctx.reply(embed=discord.Embed(title="Member Banned", description="{} was banned by {} for \"{}\".".format(memberName, ctx.author, reason), color=discord.Color.green()))
				try:
					await member.send(embed=discord.Embed(title="You Were Banned", description="You were banned from {} by {} for \"{}\".".format(ctx.guild.name, ctx.author, reason), color=discord.Color.green()))
				except:
					pass
			except Exception as exc:
				await ctx.reply(embed=discord.Embed(title="Error", description="Unable to ban member", color=discord.Color.red()))
				tragedy.logError(exc)

	@commands.command(ignore_extra=True, description="delete's specified amount of messages from channel", help="purge <amount>")
	@commands.guild_only()
	@commands.has_permissions(manage_messages=True)
	@commands.bot_has_guild_permissions(manage_messages=True)
	@commands.cooldown(1, 15, type=BucketType.member)
	async def purge(self, ctx, *amount):
		for arg in amount:
			if arg.lower() == "all":
				await ctx.channel.purge(bulk=True, limit=999999999999999999)
				try:
					cursor.execute("SELECT * FROM prefix WHERE guild=%s", (ctx.guild.id))
					temp = await ctx.send(embed=discord.Embed(title="Channel Nuked!", description="Type \"{}help\" for commands.".format(cursor.fetchone().get('prefix')), color=discord.Color.green()).set_image(url='https://media.giphy.com/media/HhTXt43pk1I1W/source.gif'))
					await asyncio.sleep(15)
					await temp.delete()
				except Exception as exc:
					tragedy.logError(exc)
			if isinstance(arg, int):
				await ctx.channel.purge(limit=arg)
				try:
					cursor.execute("SELECT * FROM prefix WHERE guild=%s", (ctx.guild.id))
					temp = await ctx.send(embed=discord.Embed(title="Channel Purged!", description="Deleted {} Messages\nType \"{}help\" for commands.".format(arg, cursor.fetchone().get('prefix')), color=discord.Color.green()).set_image(url='https://media.giphy.com/media/HhTXt43pk1I1W/source.gif'))
					await asyncio.sleep(15)
					await temp.delete()
				except Exception as exc:
					tragedy.logError(exc)

	@commands.command(description="lock's specified channel from specified role/everyone", help="lock [channel] [role]")
	@commands.guild_only()
	@commands.has_permissions(manage_channels=True)
	@commands.bot_has_permissions(manage_channels=True)
	@commands.cooldown(1, 5, commands.BucketType.member)
	async def lock(self, ctx, channel: discord.TextChannel = None, role: discord.Role = None):
		channel = channel or ctx.channel
		role = role or ctx.guild.default_role

		if ctx.guild.default_role not in channel.overwrites:
			overwrites = {
				role: discord.PermissionOverwrite(send_messages=False)
			}
			await channel.edit(overwrites=overwrites)
			embed = discord.Embed(description='{} has been locked :lock:.'.format(channel.mention), color=Color.green())
			await ctx.send(embed=embed)
		elif channel.overwrites[role].send_messages or channel.overwrites[role].send_messages == None:
			overwrites = channel.overwrites[role]
			overwrites.send_messages = False
			await channel.set_permissions(role, overwrite=overwrites)
			embed = discord.Embed(description='{} has been locked. :lock:'.format(channel.mention),color=Color.green())
			await ctx.send(embed=embed)
		else:
			overwrites = channel.overwrites[role]
			overwrites.send_messages = True
			await channel.set_permissions(role, overwrite=overwrites)
			embed = discord.Embed(description='{} has been unlocked. :unlock:'.format(channel.mention), color=Color.green())
			await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Mod(bot))

while __name__ == "__main__":
	try:
		databaseConfig.ping(reconnect=False)
	except Exception as exc:
		logging.log(logging.CRITICAL, exc)
		logging.log(logging.INFO, "Attempting to reconnect to MySQL database in '{}'".format(__file__[:-3]))
		databaseConfig = pymysql.connect(
			host=tragedy.dotenvVar("mysqlServer"),
			user="root",
			password=tragedy.dotenvVar("mysqlPassword"),
			port=3306,
			database="tragedy",
			charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor,
			read_timeout=5,
			write_timeout=5,
			connect_timeout=5,
			autocommit=True
			)