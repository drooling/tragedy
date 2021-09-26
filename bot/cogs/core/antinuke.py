# -*- coding: utf-8 -*-

import contextlib
import pprint
import random
import typing
import collections
from discord.audit_logs import AuditLogEntry
from discord.colour import Color

from discord.enums import AuditLogAction
from discord.ext.commands.converter import MemberConverter
from discord.ext.commands.core import guild_only

import bot.utils.utilities as tragedy
import discord
import pymysql.cursors
from discord.ext import commands, tasks


class AntiNuke(commands.Cog, command_attrs=dict(hidden=True)):
	def __init__(self, bot: commands.AutoShardedBot):
		self.bot = bot
		self.pool = pymysql.connect(host=tragedy.DotenvVar("mysqlServer"), user="root", password=tragedy.DotenvVar("mysqlPassword"), port=3306, database="tragedy", charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, read_timeout=5, write_timeout=5, connect_timeout=5, autocommit=True)
		self.mysqlPing.start()
		self.whitelist_cache: dict = collections.defaultdict(dict)

	@tasks.loop(seconds=35)
	async def mysqlPing(self):
		connected = bool(self.pool.open)
		pprint.pprint(
			"Testing connection to mysql database () --> {}".format(str(connected).upper()))
		if connected is False:
			self.pool.ping(reconnect=True)
			pprint.pprint("Reconnecting to database () --> SUCCESS")

	def get_whitelist(self, guild: discord.Guild) -> typing.List[int]:
		with self.pool.cursor() as cursor:
			cursor.execute("SELECT id FROM `anti-nuke-whitelist` WHERE guild=%s", (guild.id))
			rows = cursor.fetchall()
			whitelist = [entry.get("id") for entry in rows]
			return whitelist or []

	async def report_to_owner(self, guild: discord.Guild, infected: typing.Union[discord.User, discord.Member], sickness: AuditLogAction):
		emergency_embed = discord.Embed(title="EMERGENCY", color=Color.red(), description="A possible nuke attempt is being made on %s that I could not stop because I lack the permissions to do so." % (guild.name))
		emergency_embed.add_field(name="Infected User", value=infected)
		emergency_embed.add_field(name="Sickness (Actions user has taken)", value=str(sickness).title()[15:])
		await guild.owner.send(embed=emergency_embed)

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		if member.guild.id == 875514539620327454:
			if member.bot:
				whitelist = self.get_whitelist(member.guild)
				action: AuditLogEntry = (await member.guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add).flatten())[0]
				if action.user.id not in whitelist:
					inviter: discord.Member = action.user
					try:
						await member.ban(reason="tragedy Anti-Nuke | Bot Added By Non-Whitelisted User")
					except:
						await self.report_to_owner(member.guild, inviter, AuditLogAction.bot_add)
					try:
						await inviter.ban(reason="tragedy Anti-Nuke | Non-Whitelisted User Added Bot To Guild")
					except:
						await self.report_to_owner(member.guild, inviter, AuditLogAction.bot_add)

	@commands.Cog.listener()
	async def on_member_ban(self, guild: discord.Guild, user: discord.User):
		if guild.id == 875514539620327454:
			whitelist = self.get_whitelist(guild)
			action: AuditLogEntry = (await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten())[0]
			if action.user is self.bot.user:
				return
			if action.user.id not in whitelist:
				plague: discord.Member = action.user
				try:
					await plague.ban(reason="tragedy Anti-Nuke | Non-Whitelisted User Banned Member (Member has been unbanned and attempted to invite back)")
				except:
					await self.report_to_owner(guild, plague, AuditLogAction.ban)
				await guild.unban(user, reason="tragedy Anti-Nuke | Banned by Non-Whitelisted User")
				invite: discord.Invite = await random.choice(guild.text_channels).create_invite(max_uses=1, unique=True, reason="tragedy Anti-Nuke | Attempt To Re-Invite User That Was Banned By Possible Nuke")
				with contextlib.suppress(Exception):
					await user.send(content="Invite Back To %s - %s\nSorry for inconvenience you were mistakenly banned." % (guild.name, invite.url))

	@commands.Cog.listener()
	async def on_member_remove(self, user: discord.Member):
		if user.guild.id == 875514539620327454:
			whitelist = self.get_whitelist(user.guild)
			action: AuditLogEntry = (await user.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick).flatten())[0]
			if action.user is self.bot.user:
				return
			if action.user.id not in whitelist:
				plague: discord.Member = action.user
				try:
					await plague.ban(reason="tragedy Anti-Nuke | Non-Whitelisted User Kicked Member (Member attempted to invite back)")
				except:
					await self.report_to_owner(user.guild, plague, AuditLogAction.kick)
				with contextlib.suppress(Exception):
					invite: discord.Invite = await random.choice(user.guild.text_channels).create_invite(max_uses=1, unique=True, reason="tragedy Anti-Nuke | Attempt To Re-Invite User That Was Kicked By Possible Nuke")
					await user.send(content="Invite Back To %s - %s\nSorry for inconvenience you were mistakenly kicked." % (user.guild.name, invite.url))

	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel: discord.TextChannel):
		if channel.guild.id == 875514539620327454:
			whitelist = self.get_whitelist(channel.guild)
			action: AuditLogEntry = (await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete).flatten())[0]
			if action.user is self.bot.user:
				return
			if action.user.id not in whitelist:
				plague: discord.Member = action.user
				try:
					await plague.ban(reason="tragedy Anti-Nuke | Non-Whitelisted User Deleted A Channel (Channel restoration attempted)")
				except:
					await self.report_to_owner(channel.guild, plague, AuditLogAction.channel_delete)
				restore: discord.TextChannel = await channel.clone(reason="tragedy Anti-Nuke | Channel restoration attempt (Possible Nuke Attempt Cleanup)")
				await restore.edit(category=channel.category, position=channel.position, overwrites=channel.overwrites)

	@commands.group(ignore_extra=True, invoke_without_command=True)
	@tragedy.is_guild_owner()
	async def whitelist(self, ctx: commands.Context):
		current_whitelist = self.get_whitelist(ctx.guild)
		await ctx.send(embed=discord.Embed(
			title="tragedy Anti-Nuke Whitelist",
			color=Color.green(),
			description='\n'.join([ctx.guild.get_member(member).mention for member in current_whitelist])
		))

	@whitelist.command()
	async def add(self, ctx: commands.Context, member: MemberConverter):
		current_whitelist = self.get_whitelist(ctx.guild)
		if member.id in current_whitelist:
			return await ctx.reply("That user is already whitelisted !", delete_after=5)
		with self.pool.cursor() as cursor:
			cursor.execute("INSERT IGNORE INTO `anti-nuke-whitelist` (guild, id) VALUES (%s, %s)", (ctx.guild.id, member.id))
		await ctx.reply("%s has been whitelisted." % (member.mention), delete_after=5)

	@whitelist.command()
	async def remove(self, ctx: commands.Context, member: MemberConverter):
		current_whitelist = self.get_whitelist(ctx.guild)
		if member.id not in current_whitelist:
			return await ctx.reply("That user is not whitelisted.", delete_after=5)
		with self.pool.cursor() as cursor:
			cursor.execute("DELETE FROM `anti-nuke-whitelist` WHERE guild=%s AND id=%s", (ctx.guild.id, member.id))
		await ctx.reply("%s has been removed from whitelist." % (member.mention), delete_after=5)

def setup(bot):
	bot.add_cog(AntiNuke(bot))
