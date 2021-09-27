# -*- coding: utf-8 -*-

import collections
import contextlib
import pprint
import random
import typing

import bot.utils.utilities as tragedy
import discord
import pymysql.cursors
from bot.utils.classes import AntiNukeNotConfigured
from discord.audit_logs import AuditLogEntry
from discord.colour import Color
from discord.enums import AuditLogAction
from discord.ext import commands, tasks
from discord.ext.commands.converter import MemberConverter


class AntiNuke(commands.Cog):
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

	def convert_to_bool(self, int: int) -> bool:
		return (False if int == 0 else True)

	def convert_to_action(self, int: int) -> typing.Union[discord.Member.ban, discord.Member.kick]:
		return (discord.Member.ban if int == 0 else discord.Member.kick)

	def get_whitelist(self, guild: discord.Guild) -> typing.List[int]:
		with self.pool.cursor() as cursor:
			cursor.execute("SELECT id FROM `anti-nuke-whitelist` WHERE guild=%s", (guild.id))
			rows = cursor.fetchall()
			whitelist = [entry.get("id") for entry in rows]
			return whitelist or []

	def get_config(self, guild: discord.Guild) -> typing.Tuple:
		with self.pool.cursor() as cursor:
			cursor.execute("SELECT `self_bot`, `punishment` FROM `anti-nuke` WHERE guild=%s", (guild.id))
			row = cursor.fetchone()
			try:
				return (self.convert_to_bool(row.get("self_bot")), self.convert_to_action(row.get('punishment')))
			except AttributeError:
				raise AntiNukeNotConfigured()

	async def report_to_owner(self, guild: discord.Guild, infected: typing.Union[discord.User, discord.Member], sickness: AuditLogAction):
		emergency_embed = discord.Embed(title="EMERGENCY", color=Color.red(), description="A possible nuke attempt is being made on %s that I could not stop because I lack the permissions to do so." % (guild.name))
		emergency_embed.add_field(name="Infected User", value=infected)
		emergency_embed.add_field(name="Sickness (Actions user has taken)", value=str(sickness).replace('_', ' ').title()[15:])
		await guild.owner.send(embed=emergency_embed),

	#@commands.Cog.listener()
	#async def on_message(self, message: discord.Message):
	#	if message.nonce is None and message.author.bot == False:
	#		punishment = (self.get_config(message.guild))[1]
	#		await punishment(message.author, reason="tragedy2cool")

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		if member.guild.id == 875514539620327454:
			if member.bot:
				punishment = (self.get_config(member.guild))[1]
				whitelist = self.get_whitelist(member.guild)
				action: AuditLogEntry = (await member.guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add).flatten())[0]
				if action.user.id not in whitelist:
					inviter: discord.Member = action.user
					try:
						await punishment(member, reason="tragedy Anti-Nuke | Bot Added By Non-Whitelisted User")
					except:
						await self.report_to_owner(member.guild, inviter, AuditLogAction.bot_add)
					try:
						await punishment(inviter, reason="tragedy Anti-Nuke | Non-Whitelisted User Added Bot To Guild")
					except:
						await self.report_to_owner(member.guild, inviter, AuditLogAction.bot_add)

	@commands.Cog.listener()
	async def on_member_ban(self, guild: discord.Guild, user: discord.User):
		if guild.id == 875514539620327454:
			punishment = (self.get_config(user.guild))[1]
			whitelist = self.get_whitelist(guild)
			action: AuditLogEntry = (await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten())[0]
			if action.user.id == self.bot.user.id:
				return
			if action.user.id not in whitelist:
				plague: discord.Member = action.user
				try:
					await punishment(plague, reason="tragedy Anti-Nuke | Non-Whitelisted User Banned Member (Member has been unbanned and attempted to invite back)")
				except:
					await self.report_to_owner(guild, plague, AuditLogAction.ban)
				await guild.unban(user, reason="tragedy Anti-Nuke | Banned by Non-Whitelisted User")
				invite: discord.Invite = await random.choice(guild.text_channels).create_invite(max_uses=1, unique=True, reason="tragedy Anti-Nuke | Attempt To Re-Invite User That Was Banned By Possible Nuke")
				with contextlib.suppress(Exception):
					await user.send(content="Invite Back To %s - %s\nSorry for inconvenience you were mistakenly banned." % (guild.name, invite.url))

	@commands.Cog.listener()
	async def on_member_remove(self, user: discord.Member):
		if user.guild.id == 875514539620327454:
			punishment = (self.get_config(user.guild))[1]
			whitelist = self.get_whitelist(user.guild)
			action: AuditLogEntry = (await user.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick).flatten())[0]
			if action.user.id == self.bot.user.id:
				return
			if action.user.id not in whitelist:
				plague: discord.Member = action.user
				try:
					await punishment(plague, reason="tragedy Anti-Nuke | Non-Whitelisted User Kicked Member (Member attempted to invite back)")
				except:
					await self.report_to_owner(user.guild, plague, AuditLogAction.kick)
				with contextlib.suppress(Exception):
					invite: discord.Invite = await random.choice(user.guild.text_channels).create_invite(max_uses=1, unique=True, reason="tragedy Anti-Nuke | Attempt To Re-Invite User That Was Kicked By Possible Nuke")
					await user.send(content="Invite Back To %s - %s\nSorry for inconvenience you were mistakenly kicked." % (user.guild.name, invite.url))

	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel: discord.TextChannel):
		if channel.guild.id == 875514539620327454:
			punishment = (self.get_config(channel.guild))[1]
			whitelist = self.get_whitelist(channel.guild)
			action: AuditLogEntry = (await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete).flatten())[0]
			if action.user.id == self.bot.user.id:
				return
			if action.user.id not in whitelist:
				plague: discord.Member = action.user
				try:
					await punishment(plague, reason="tragedy Anti-Nuke | Non-Whitelisted User Deleted A Channel (Channel restoration attempted)")
				except Exception as e:
					print(e)
					await self.report_to_owner(channel.guild, plague, AuditLogAction.channel_delete)
				restore: discord.TextChannel = await channel.clone(reason="tragedy Anti-Nuke | Channel restoration attempt (Possible Nuke Attempt Cleanup)")
				await restore.edit(category=channel.category, position=channel.position, overwrites=channel.overwrites)

	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel: discord.TextChannel):
		if channel.guild.id == 875514539620327454:
			punishment = (self.get_config(channel.guild))[1]
			whitelist = self.get_whitelist(channel.guild)
			action: AuditLogEntry = (await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create).flatten())[0]
			if action.user.id == self.bot.user.id:
				return
			if action.user.id not in whitelist:
				plague: discord.Member = action.user
				try:
					await punishment(plague, reason="tragedy Anti-Nuke | Non-Whitelisted User Created A Channel (Channel cleanup attempted)")
				except:
					await self.report_to_owner(channel.guild, plague, AuditLogAction.channel_create)
				await channel.delete(reason="tragedy Anti-Nuke | Channel cleanup attempt (Possible Nuke Attempt Cleanup)")

	@commands.Cog.listener()
	async def on_guild_role_delete(self, role: discord.Role):
		if role.guild.id == 875514539620327454:
			punishment = (self.get_config(role.guild))[1]
			whitelist = self.get_whitelist(role.guild)
			action: AuditLogEntry = (await role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete).flatten())[0]
			if action.user.id == self.bot.user.id:
				return
			if action.user.id not in whitelist:
				plague: discord.Member = action.user
				try:
					await punishment(plague, reason="tragedy Anti-Nuke | Non-Whitelisted User Deleted A Role (Role restoration attempted)")
				except:
					await self.report_to_owner(role.guild, plague, AuditLogAction.role_delete)
				await role.guild.create_role(reason="tragedy Anti-Nuke | Role restoration attempt (Possible Nuke Attempt Cleanup)", name=role.name, permissions=role.permissions, color=role.color, hoist=role.hoist, mentionable=role.mentionable)
	
	@commands.Cog.listener()
	async def on_guild_role_create(self, role: discord.Role):
		if role.guild.id == 875514539620327454:
			punishment = (self.get_config(role.guild))[1]
			whitelist = self.get_whitelist(role.guild)
			action: AuditLogEntry = (await role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete).flatten())[0]
			if action.user.id == self.bot.user.id:
				return
			if action.user.id not in whitelist:
				plague: discord.Member = action.user
				try:
					await punishment(plague, reason="tragedy Anti-Nuke | Non-Whitelisted User Created A Role (Role cleanup attempted)")
				except:
					await self.report_to_owner(role.guild, plague, AuditLogAction.role_delete)
				await role.guild.create_role(reason="tragedy Anti-Nuke | Role cleanup attempt (Possible Nuke Attempt Cleanup)", name=role.name, permissions=role.permissions, color=role.color, hoist=role.hoist, mentionable=role.mentionable)

#	@commands.Cog.listener()
#	async def on_webhooks_update(self, channel: discord.Webhook):
#		if channel.guild.id == 875514539620327454:
#			whitelist = self.get_whitelist(channel.guild)
#			action: AuditLogEntry = (await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.webhook_delete).flatten())[0]
#			if action.user.id == self.bot.user.id:
#				return
#			if action.user.id not in whitelist:
#				plague: discord.Member = action.user
#				try:
#					await plague.ban(reason="tragedy Anti-Nuke | Non-Whitelisted User Deleted A Webhook")
#				except:
#					await self.report_to_owner(channel.guild, plague, AuditLogAction.webhook_delete)

	@commands.group(ignore_extra=True, invoke_without_command=True)
	@tragedy.is_guild_owner()
	async def antinuke(self, ctx: commands.Context):
		config = self.get_config(ctx.guild)
		embed = discord.Embed(title="tragedy Anti-Nuke", color=Color.green(), description="Anti-Nuke is configured to `%s` infected members and self-bot punishments are %s." % ("Ban" if config[1] == discord.Member.ban else "kick", "Enabled" if config[0] == True else "Disabled"))
		await ctx.send(embed=embed)

	@antinuke.command()
	async def enable(self, ctx: commands.Context):
		with self.pool.cursor() as cursor:
			cursor.execute("INSERT IGNORE INTO `anti-nuke` (guild) VALUES (%s)", (ctx.guild.id))
		await ctx.reply("tragedy Anti-Nuke has been enabled.", delete_after=5)

	@antinuke.command()
	async def disable(self, ctx: commands.Context):
		with self.pool.cursor() as cursor:
			cursor.execute("DELETE FROM `anti-nuke` WHERE guild=%s", (ctx.guild.id))
		await ctx.reply("tragedy Anti-Nuke has been disabled.", delete_after=5)

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
