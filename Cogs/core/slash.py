# -*- coding: utf-8 -*-

from discord.activity import Spotify
import resources.utilities as tragedy
import asyncio
from datetime import datetime
from discord.colour import Color
from discord.ext import commands
import discord
from dislash import *
import timeago

class Slash(commands.Cog, command_attrs=dict(hidden=True)):
	def __init__(self, bot):
		self.bot = bot

	@slash_commands.command(
		name="whois",
		description="Gives details about specified user",
		options=[
			Option("member", "Specify any user", Type.USER, required=True),
		]
	)
	async def whois(self, ctx, member: discord.Member = None):
		member = member if member != None else ctx.author
		joinPosition = sum(m.joined_at < member.joined_at for m in ctx.guild.members if m.joined_at is not None)
		roleNameList = list(role.mention for role in member.roles if role != ctx.guild.default_role)
		#userProfile = await member.profile() User profile has been depracated since v1.7
		#externalAccounts = list("Type: {} - Username: {}".format(external.get("type", "Error"), external.get("name", "Error")) for external in await userProfile.connected_accounts) User profile has been depracated since v1.7
		embed = discord.Embed(color=Color.green(), timestamp=datetime.now())
		embed.set_author(name="{} ({})".format(member, member.id), icon_url=member.avatar_url)
		embed.add_field(name="Basic Info", value="Joined Server At - **{} (Around {})**\nRegistered on Discord At - **{} (Around {})**".format(member.joined_at.strftime("%A, %#d %B %Y, %I:%M %p"), timeago.format(datetime.now() - member.joined_at), member.created_at.strftime('%A, %#d %B %Y, %I:%M %p'), timeago.format(datetime.now() - member.created_at)))
		embed.add_field(name="Status Info", value="Desktop Status - **{}**\nMobile Status - **{}**\nWeb Application Status - **{}**".format(tragedy.humanStatus(str(member.desktop_status)), tragedy.humanStatus(str(member.mobile_status)), tragedy.humanStatus(str(member.web_status))), inline=False)
		embed.add_field(name="Role Info", value="Top Role - {}\nRole(s) - {}".format(member.top_role.mention if member.top_role != ctx.guild.default_role else "None", ', '.join(roleNameList).removesuffix(', ') if roleNameList != [] else "None"), inline=False)
		embed.add_field(name="Flags", value="{} - Discord Staff\n{} - Discord Partner\n{} - Verified Bot Developer".format(tragedy.EmojiBool(member.public_flags.staff), tragedy.EmojiBool(member.public_flags.partner), tragedy.EmojiBool(member.public_flags.verified_bot_developer)))
		#embed.add_field(name="Other Info", value="HypeSquad House - {}\nUser has Nitro - {}\nConnected Accounts - {}".format(str(userProfile.hypesquad_houses).title(), tragedy.EmojiBool(await userProfile.nitro), ', '.join(externalAccounts).removeprefix(', ') if externalAccounts != [] else "None")) User profile has been depracated since v1.7
		embed.set_footer(icon_url=ctx.author.avatar_url, text='Requested By: {}'.format(ctx.author.name))
		temp = await ctx.send(embed=embed)
		await asyncio.sleep(15)
		await temp.delete()

	@slash_commands.command(
		name="spotify",
		description="Gives details about what specified user is currently listening to on Spotify",
		options=[
			Option("member", "Specify any user", Type.USER, required=True)
		]
	)
	async def spotify(self, ctx, member: discord.Member):
		try:
			for activity in member.activities:
				if isinstance(activity, Spotify):
					embed = discord.Embed(title="Spotify", color=activity.color)
					embed.set_author(name=member, icon_url="https://discord.com/assets/f0655521c19c08c4ea4e508044ec7d8c.png")
					embed.set_thumbnail(url=activity.album_cover_url)
					embed.add_field(name="Song Title", value=activity.title)
					embed.add_field(name="Song Album", value=activity.album)
					embed.add_field(name="Song Artist(s)", value=', '.join(activity.artists).removeprefix(', '), inline=False)
					embed.add_field(name="Song Length", value="{}:{}".format((activity.duration.seconds % 3600) // 60, activity.duration.seconds % 60), inline=False)
					embed.add_field(name="Party ID", value=activity.party_id)
					embed.add_field(name="Track ID", value=activity.track_id)
					temp = await ctx.send(embed=embed)
					await asyncio.sleep(15)
					await temp.delete()
				else:
					pass
			if "Spotify" not in str(member.activities):
				embed = discord.Embed(title="Error", description="That user is not listening to Spotify at the moment you silly goose.", color=Color.red())
				temp = await ctx.send(embed=embed)
				await asyncio.sleep(15)
				await temp.delete()
		except Exception as exc:
			print("[Exception] {}".format(exc))

	@slash_commands.command(
		name="serverinfo",
		description="Gives details about current guild"
	)
	async def server(self, ctx):
		findbots = sum(1 for member in ctx.guild.members if member.bot)
		vanity = "VANITY_URL" in str(ctx.guild.features)
		splash = "INVITE_SPLASH" in str(ctx.guild.features)
		animicon = "ANIMATED_ICON" in str(ctx.guild.features)
		discoverable = "DISCOVERY" in str(ctx.guild.features)
		banner = "BANNER" in str(ctx.guild.features)
		vanityFeature = "{} - Vanity URL".format(tragedy.EmojiBool(vanity)) if not vanity else "{} - Vanity URL ({})".format(vanity, await ctx.guild.vanity_url)
		embed = discord.Embed(title = '**{}**'.format(ctx.guild.name), colour = Color.green(), timestamp=datetime.now())
		embed.set_thumbnail(url=str(ctx.guild.icon_url))
		embed.add_field(name = "Members", value="Bots: **{}**\nHumans: **{}**\nOnline Members: **{}/{}**".format(str(findbots), ctx.guild.member_count - findbots, sum(member.status!=discord.Status.offline and not member.bot for member in ctx.guild.members), str(ctx.guild.member_count)))
		embed.add_field(name = "Channels", value=":speech_balloon: Text Channels: **{}**\n:loud_sound: Voice Channels: **{}**".format(len(ctx.guild.text_channels), len(ctx.guild.voice_channels)))
		embed.add_field(name = "Important Info", value="Owner: {}\nVerification Level: **{}**\nGuild ID: **{}**".format(ctx.guild.owner.mention, str(ctx.guild.verification_level).title(), ctx.guild.id), inline=False)
		embed.add_field(name = "Other Info", value="AFK Channel: **{}**\n AFK Timeout: **{} minute(s)**\nCustom Emojis: **{}**\nRole Count: **{}**\nFilesize Limit - **{}**".format(ctx.guild.afk_channel, str(ctx.guild.afk_timeout / 60), len(ctx.guild.emojis), len(ctx.guild.roles), tragedy.humansize(ctx.guild.filesize_limit)), inline=False)
		embed.add_field(name = "Server Features", value="{} - Banner\n{}\n{} - Splash Invite\n{} - Animated Icon\n{} - Server Discoverable".format(tragedy.EmojiBool(banner), vanityFeature, tragedy.EmojiBool(splash), tragedy.EmojiBool(animicon), tragedy.EmojiBool(discoverable)))
		embed.add_field(name = "Nitro Info", value="Number of Boosts - **{}**\nBooster Role - **{}**\nBoost Level/Tier - **{}**".format(str(ctx.guild.premium_subscription_count), ctx.guild.premium_subscriber_role.mention if ctx.guild.premium_subscriber_role != None else ctx.guild.premium_subscriber_role, ctx.guild.premium_tier))
		temp = await ctx.send(embed=embed)
		await asyncio.sleep(15)
		await temp.delete()


def setup(bot):
	bot.add_cog(Slash(bot))