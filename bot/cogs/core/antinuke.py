# -*- coding: utf-8 -*-

import collections
import contextlib
from datetime import datetime
import io
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
			"Testing connection to mysql database () --> {} IN {}".format(str(connected).upper(), __file__))
		if connected is False:
			self.pool.ping(reconnect=True)
			pprint.pprint("Reconnecting to database () --> SUCCESS")

	def convert_to_bool(self, int: int) -> bool:
		return (False if int == 0 else True)

	def convert_to_action(self, int: int) -> typing.Union[discord.Member.ban, discord.Member.kick]:
		return (discord.Member.ban if int == 0 else discord.Member.kick)

	def _get_whitelist(self, guild: discord.Guild) -> typing.List[int]:
		with self.pool.cursor() as cursor:
			cursor.execute("SELECT id FROM `anti-nuke-whitelist` WHERE guild=%s", (guild.id))
			rows = cursor.fetchall()
			whitelist = [entry.get("id") for entry in rows]
			return list(set(whitelist)) or []

	def get_whitelist(self, guild: discord.Guild) -> typing.List[int]:
		try:
			if guild.id in self.whitelist_cache:
				return self.whitelist_cache[guild.id]
			else:
				whitelist = self._get_whitelist(guild)
				self.whitelist_cache[guild.id] = whitelist
				return whitelist
		except:
			return self._get_whitelist(guild)

	def get_config(self, guild: discord.Guild) -> typing.Tuple:
		with self.pool.cursor() as cursor:
			try:
				cursor.execute("SELECT `self_bot`, `Punishment` FROM `anti-nuke` WHERE guild=%s", (guild.id))
				row = cursor.fetchone()
				return (self.convert_to_bool(row.get("self_bot")), self.convert_to_action(row.get('Punishment')))
			except Exception:
				raise AntiNukeNotConfigured()

	async def report_to_owner(self, guild: discord.Guild, infected: typing.Union[discord.User, discord.Member], sickness: AuditLogAction):
		emergency_embed = discord.Embed(title="EMERGENCY", color=Color.red(), description="A possible nuke attempt is being made on %s." % (guild.name))
		emergency_embed.add_field(name="Infected User", value=infected)
		emergency_embed.add_field(name="Sickness (Actions user has taken)", value=str(sickness).replace('_', ' ').title()[15:])
		emergency_embed.add_field(name="Time", value="<t:{}:f>".format(int(datetime.now().timestamp())))
		await guild.owner.send(embed=emergency_embed)

	@commands.Cog.listener()
	async def on_message(self, message: discord.Message):
		try:
			self.get_config(message.guild)
		except Exception:
			return
		config = self.get_config(message.guild)
		Punishment = (config)[1]
		selfbot = (config)[0]
		if message.nonce is None and message.author.bot == False and selfbot == True and message.is_system == False:
			try:
				await Punishment(message.author, reason="tragedy Anti-Nuke | User possibly using a self-bot.")
			except:
				await self.report_to_owner(message.guild, message.author, AuditLogAction.bot_add)

	#@commands.Cog.listener()
	#async def on_member_update(self, before: discord.Member, after: discord.Member):
	#	try:
	#		self.get_config(after.guild)
	#	except AntiNukeNotConfigured:
	#		return
	#	new_role: discord.Role = list(set(after.roles).difference(before.roles))[0]
	#	Punishment = (self.get_config(after.guild))[1]
	#	whitelist = self.get_whitelist(after.guild)
	#	action: AuditLogEntry = (await after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update).flatten())[0]
	#	if action.user.id == after.guild.owner.id:
	#		return
	#	if action.user.id == self.bot.user.id:
	#		return
	#	if action.user.id not in whitelist:
	#		if new_role.permissions in (discord.Permissions.administrator()):
	#			plague: discord.Member = action.user
	#			try:
	#				await Punishment(plague, reason="tragedy Anti-Nuke | Non-Whitelisted User Gave Another User An Admin Role (Cleanup Attempted)")
	#			except:
	#				await self.report_to_owner(before.guild, plague, AuditLogAction.member_role_update)
	#			await after.remove_roles(new_role, reason="tragedy Anti-Nuke | Cleanup Attempt")

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		try:
			self.get_config(member.guild)
		except Exception:
			return
		if member.bot:
			Punishment = (self.get_config(member.guild))[1]
			whitelist = self.get_whitelist(member.guild)
			action: AuditLogEntry = (await member.guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add).flatten())[0]
			if action.user.id == member.guild.owner.id:
				return
			if action.user.id not in whitelist:
				inviter: discord.Member = action.user
				try:
					await Punishment(member, reason="tragedy Anti-Nuke | Bot Added By Non-Whitelisted User")
				except:
					await self.report_to_owner(member.guild, inviter, AuditLogAction.bot_add)
				try:
					await Punishment(inviter, reason="tragedy Anti-Nuke | Non-Whitelisted User Added Bot To Guild")
				except:
					await self.report_to_owner(member.guild, inviter, AuditLogAction.bot_add)

	@commands.Cog.listener()
	async def on_member_ban(self, guild: discord.Guild, user: discord.User):
		try:
			self.get_config(guild)
		except Exception:
			return
		Punishment = (self.get_config(guild))[1]
		whitelist = self.get_whitelist(guild)
		action: AuditLogEntry = (await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten())[0]
		if action.user.id == guild.owner.id:
			return
		if action.user.id == self.bot.user.id:
			return
		if action.user.id not in whitelist:
			plague: discord.Member = action.user
			try:
				await Punishment(plague, reason="tragedy Anti-Nuke | Non-Whitelisted User Banned Member (Member has been unbanned and attempted to invite back)")
			except:
				await self.report_to_owner(guild, plague, AuditLogAction.ban)
			await guild.unban(user, reason="tragedy Anti-Nuke | Banned by Non-Whitelisted User")
			invite: discord.Invite = await random.choice(guild.text_channels).create_invite(max_uses=1, unique=True, reason="tragedy Anti-Nuke | Attempt To Re-Invite User That Was Banned By Possible Nuke")
			with contextlib.suppress(Exception):
				await user.send(content="Invite Back To %s - %s\nSorry for inconvenience you were mistakenly banned." % (guild.name, invite.url))

	@commands.Cog.listener()
	async def on_member_remove(self, user: discord.Member):
		try:
			self.get_config(user.guild)
		except Exception:
			return
		Punishment = (self.get_config(user.guild))[1]
		whitelist = self.get_whitelist(user.guild)
		action: AuditLogEntry = (await user.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick).flatten())[0]
		if action.user.id == user.guild.owner.id:
			return
		if action.user.id == self.bot.user.id:
			return
		if action.user.id not in whitelist:
			plague: discord.Member = action.user
			try:
				await Punishment(plague, reason="tragedy Anti-Nuke | Non-Whitelisted User Kicked Member (Member attempted to invite back)")
			except:
				await self.report_to_owner(user.guild, plague, AuditLogAction.kick)
			with contextlib.suppress(Exception):
				invite: discord.Invite = await random.choice(user.guild.text_channels).create_invite(max_uses=1, unique=True, reason="tragedy Anti-Nuke | Attempt To Re-Invite User That Was Kicked By Possible Nuke")
				await user.send(content="Invite Back To %s - %s\nSorry for inconvenience you were mistakenly kicked." % (user.guild.name, invite.url))

	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel: discord.TextChannel):
		try:
			self.get_config(channel.guild)
		except Exception:
			return
		Punishment = (self.get_config(channel.guild))[1]
		whitelist = self.get_whitelist(channel.guild)
		action: AuditLogEntry = (await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete).flatten())[0]
		if action.user.id == channel.guild.owner.id:
			return
		if action.user.id == self.bot.user.id:
			return
		if action.user.id not in whitelist:
			plague: discord.Member = action.user
			try:
				await Punishment(plague, reason="tragedy Anti-Nuke | Non-Whitelisted User Deleted A Channel (Channel restoration attempted)")
			except:
				await self.report_to_owner(channel.guild, plague, AuditLogAction.channel_delete)
			restore: discord.TextChannel = await channel.clone(reason="tragedy Anti-Nuke | Channel restoration attempt (Possible Nuke Attempt Cleanup)")
			await restore.edit(category=channel.category, position=channel.position, overwrites=channel.overwrites)

	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel: discord.TextChannel):
		try:
			self.get_config(channel.guild)
		except Exception:
			return
		Punishment = (self.get_config(channel.guild))[1]
		whitelist = self.get_whitelist(channel.guild)
		action: AuditLogEntry = (await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create).flatten())[0]
		if action.user.id == channel.guild.owner.id:
			return
		if action.user.id == self.bot.user.id:
			return
		if action.user.id not in whitelist:
			plague: discord.Member = action.user
			try:
				await Punishment(plague, reason="tragedy Anti-Nuke | Non-Whitelisted User Created A Channel (Channel cleanup attempted)")
			except:
				await self.report_to_owner(channel.guild, plague, AuditLogAction.channel_create)
			await channel.delete(reason="tragedy Anti-Nuke | Channel cleanup attempt (Possible Nuke Attempt Cleanup)")

	@commands.Cog.listener()
	async def on_guild_role_delete(self, role: discord.Role):
		try:
			self.get_config(role.guild)
		except Exception:
			return
		Punishment = (self.get_config(role.guild))[1]
		whitelist = self.get_whitelist(role.guild)
		action: AuditLogEntry = (await role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete).flatten())[0]
		if action.user.id == role.guild.owner.id:
			return
		if action.user.id == self.bot.user.id:
			return
		if action.user.id not in whitelist:
			plague: discord.Member = action.user
			try:
				await Punishment(plague, reason="tragedy Anti-Nuke | Non-Whitelisted User Deleted A Role (Role restoration attempted)")
			except:
				await self.report_to_owner(role.guild, plague, AuditLogAction.role_delete)
			restore = await role.guild.create_role(reason="tragedy Anti-Nuke | Role restoration attempt (Possible Nuke Attempt Cleanup)", name=role.name, permissions=role.permissions, color=role.color, hoist=role.hoist, mentionable=role.mentionable)
			await role.guild.edit_role_postions(positions={restore: role.position}, reason="tragedy Anti-Nuke | Role restoration attempt (Possible Nuke Attempt Cleanup)")

	@commands.Cog.listener()
	async def on_guild_role_create(self, role: discord.Role):
		try:
			self.get_config(role.guild)
		except Exception:
			return
		Punishment = (self.get_config(role.guild))[1]
		whitelist = self.get_whitelist(role.guild)
		action: AuditLogEntry = (await role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create).flatten())[0]
		if action.user.id == role.guild.owner.id:
			return
		if action.user.id == self.bot.user.id:
			return
		if action.user.id not in whitelist:
			plague: discord.Member = action.user
			try:
				await Punishment(plague, reason="tragedy Anti-Nuke | Non-Whitelisted User Created A Role (Role cleanup attempted)")
			except:
				await self.report_to_owner(role.guild, plague, AuditLogAction.role_create)
			await role.delete(reason="tragedy Anti-Nuke | Role Cleanup Attempt")

	@commands.Cog.listener()
	async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
		try:
			self.get_config(after)
		except Exception:
			return
		Punishment = (self.get_config(after))[1]
		whitelist = self.get_whitelist(after)
		action: AuditLogEntry = (await after.audit_logs(limit=1, action=discord.AuditLogAction.guild_update).flatten())[0]
		if action.user.id == after.owner.id:
			return
		if action.user.id == self.bot.user.id:
			return
		if action.user.id not in whitelist:
			plague: discord.Member = action.user
			try:
				await Punishment(plague, reason="tragedy Anti-Nuke | Non-Whitelisted User Modified Guild (Restoration Attempted)")
			except:
				await self.report_to_owner(before, plague, AuditLogAction.guild_update)
			await after.edit(reason="tragedy Anti-Nuke | Restoration Attempt", name=before.name, description=before.description)

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
	@commands.guild_only()
	async def antinuke(self, ctx: commands.Context):
		if ctx.author.id != ctx.guild.owner.id:
			raise tragedy.NotGuildOwner()
		config = self.get_config(ctx.guild)
		embed = discord.Embed(title="tragedy Anti-Nuke", color=Color.green(), description="Anti-Nuke is configured to `%s` infected members and self-bot Punishments are %s." % ("ban" if config[1] == discord.Member.ban else "kick", "enabled" if config[0] == True else "disabled"))
		await ctx.send(embed=embed)

	@antinuke.command()
	async def enable(self, ctx: commands.Context):
		if ctx.author.id != ctx.guild.owner.id:
			raise tragedy.NotGuildOwner()
		with self.pool.cursor() as cursor:
			cursor.execute("INSERT IGNORE INTO `anti-nuke` (guild) VALUES (%s)", (ctx.guild.id))
		await ctx.reply("tragedy Anti-Nuke has been enabled.", delete_after=5)

	@antinuke.command()
	async def disable(self, ctx: commands.Context):
		if ctx.author.id != ctx.guild.owner.id:
			raise tragedy.NotGuildOwner()
		with self.pool.cursor() as cursor:
			cursor.execute("DELETE FROM `anti-nuke` WHERE guild=%s", (ctx.guild.id))
		del self.whitelist_cache[ctx.guild.id]
		await ctx.reply("tragedy Anti-Nuke has been disabled.", delete_after=5)

	@antinuke.command()
	async def punishment(self, ctx: commands.Context, *, Punishment: str):
		if ctx.author.id != ctx.guild.owner.id:
			raise tragedy.NotGuildOwner()
		with self.pool.cursor() as cursor:
			if Punishment.casefold() == "ban":
				cursor.execute("UPDATE `anti-nuke` SET Punishment=%s WHERE guild=%s", (0, ctx.guild.id))
			elif Punishment.casefold() == "kick":
				cursor.execute("UPDATE `anti-nuke` SET Punishment=%s WHERE guild=%s", (1, ctx.guild.id))
			else:
				return await ctx.send("The Punishment options are `ban` or `kick` only.", delete_after=5)
			await ctx.reply("Punishment has been changed.", delete_after=5)

	@antinuke.command()
	async def selfbot(self, ctx: commands.Context, *, enabled: str):
		if ctx.author.id != ctx.guild.owner.id:
			raise tragedy.NotGuildOwner()
		with self.pool.cursor() as cursor:
			if enabled.casefold() == "off":
				cursor.execute("UPDATE `anti-nuke` SET self_bot=%s WHERE guild=%s", (0, ctx.guild.id))
			elif enabled.casefold() == "on":
				cursor.execute("UPDATE `anti-nuke` SET self_bot=%s WHERE guild=%s", (1, ctx.guild.id))
			else:
				return await ctx.send("The Punishment options are `on` or `off` only.", delete_after=5)
			await ctx.reply("Self-bot Punishment has been changed.", delete_after=5)

	@commands.group(ignore_extra=True, invoke_without_command=True)
	@tragedy.is_guild_owner()
	async def whitelist(self, ctx: commands.Context):
		if ctx.author.id != ctx.guild.owner.id:
			raise tragedy.NotGuildOwner()
		current_whitelist = self.get_whitelist(ctx.guild)
		await ctx.send(embed=discord.Embed(
			title="tragedy Anti-Nuke Whitelist",
			color=Color.green(),
			description='\n'.join([ctx.guild.get_member(member).mention for member in current_whitelist]) or "Nobody is whitelisted."
		))

	@whitelist.command()
	async def add(self, ctx: commands.Context, member: MemberConverter):
		if ctx.author.id != ctx.guild.owner.id:
			raise tragedy.NotGuildOwner()
		current_whitelist = self.get_whitelist(ctx.guild)
		if member.id in current_whitelist:
			return await ctx.reply("That user is already whitelisted !", delete_after=5)
		with self.pool.cursor() as cursor:
			cursor.execute("INSERT IGNORE INTO `anti-nuke-whitelist` (guild, id) VALUES (%s, %s)", (ctx.guild.id, member.id))
		del self.whitelist_cache[ctx.guild.id]
		await ctx.reply("%s has been whitelisted." % (member.mention), delete_after=5)

	@whitelist.command()
	async def remove(self, ctx: commands.Context, member: MemberConverter):
		if ctx.author.id != ctx.guild.owner.id:
			raise tragedy.NotGuildOwner()
		current_whitelist = self.get_whitelist(ctx.guild)
		if member.id not in current_whitelist:
			return await ctx.reply("That user is not whitelisted.", delete_after=5)
		with self.pool.cursor() as cursor:
			cursor.execute("DELETE FROM `anti-nuke-whitelist` WHERE guild=%s AND id=%s", (ctx.guild.id, member.id))
		del self.whitelist_cache[ctx.guild.id]
		await ctx.reply("%s has been removed from whitelist." % (member.mention), delete_after=5)

def setup(bot):
	bot.add_cog(AntiNuke(bot))