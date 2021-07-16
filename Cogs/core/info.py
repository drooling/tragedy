# -*- coding: utf-8 -*-

import asyncio
from datetime import datetime
import resources.utilities as tragedy
from discord.colour import Color
from discord.ext import commands
import discord
from discord.ext.commands.cooldowns import BucketType
import timeago
from discord.activity import *
import aiohttp

class Info(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.aiohttp = aiohttp.ClientSession()

	@commands.command()
	@commands.cooldown(1, 5, type=BucketType.member)
	async def whois(self, ctx, member: discord.Member = None):
		member = member if member != None else ctx.author
		joinPosition = sum(m.joined_at < member.joined_at for m in ctx.guild.members if m.joined_at is not None)
		roleNameList = list(role.mention for role in member.roles if role != ctx.guild.default_role)
		#userProfile = await self.bot.fetch_user_profile(member.id) User profile has been depracated since v1.7
		#externalAccounts = list("Type: {} - Username: {}".format(external.get("type", "Error"), external.get("name", "Error")) for external in await userProfile.connected_accounts) User profile has been depracated since v1.7
		embed = discord.Embed(color=Color.green(), timestamp=datetime.utcnow())
		embed.set_author(name="{} ({})".format(member, member.id), icon_url=member.avatar_url)
		embed.add_field(name="Basic Info", value="Joined Server At - **{} (Around {})**\nRegistered on Discord At - **{} (Around {})**".format(member.joined_at.strftime("%A, %#d %B %Y, %I:%M %p"), timeago.format(datetime.now() - member.joined_at), member.created_at.strftime('%A, %#d %B %Y, %I:%M %p'), timeago.format(datetime.now() - member.created_at)))
		embed.add_field(name="Status Info", value="Desktop Status - **{}**\nMobile Status - **{}**\nWeb Application Status - **{}**".format(tragedy.humanStatus(str(member.desktop_status)), tragedy.humanStatus(str(member.mobile_status)), tragedy.humanStatus(str(member.web_status))), inline=False)
		embed.add_field(name="Role Info", value="Top Role - {}\nRole(s) - {}".format(member.top_role.mention if member.top_role != ctx.guild.default_role else "None", ', '.join(roleNameList).removesuffix(', ') if roleNameList != [] else "None"), inline=False)
		embed.add_field(name="Flags", value="{} - Discord Staff\n{} - Discord Partner\n{} - Verified Bot Developer".format(tragedy.EmojiBool(member.public_flags.staff), tragedy.EmojiBool(member.public_flags.partner), tragedy.EmojiBool(member.public_flags.verified_bot_developer)))
		#embed.add_field(name="Other Info", value="HypeSquad House - {}\nUser has Nitro - {}\nConnected Accounts - {}".format(str(userProfile.hypesquad_houses).title(), tragedy.EmojiBool(await userProfile.nitro), ', '.join(externalAccounts).removeprefix(', ') if externalAccounts != [] else "None")) User profile has been depracated since v1.7
		embed.set_footer(icon_url=ctx.author.avatar_url, text='Requested By: {}'.format(ctx.author.name))
		temp = await ctx.reply(embed=embed, mention_author=True)
		await asyncio.sleep(15)
		await temp.delete()
		await ctx.message.delete()

	@commands.command(aliases=["guild", "si", "serverinfo", "guildinfo"])
	@commands.cooldown(1, 5, type=BucketType.member)
	async def server(self, ctx):
		findbots = sum(1 for member in ctx.guild.members if member.bot)
		vanity = "VANITY_URL" in str(ctx.guild.features)
		splash = "INVITE_SPLASH" in str(ctx.guild.features)
		animicon = "ANIMATED_ICON" in str(ctx.guild.features)
		discoverable = "DISCOVERY" in str(ctx.guild.features)
		banner = "BANNER" in str(ctx.guild.features)
		vanityFeature = "{} - Vanity URL".format(tragedy.EmojiBool(vanity)) if not vanity else "{} - Vanity URL ({})".format(vanity, await ctx.guild.vanity_url)
		embed = discord.Embed(title = '**{}**'.format(ctx.guild.name), colour = Color.green(), timestamp=datetime.utcnow())
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
		await ctx.message.delete()

	@commands.command()
	@commands.cooldown(1, 5, type=BucketType.member)
	async def spotify(self, ctx, member: discord.Member = None):
		member = member if member != None else ctx.author
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
					temp = await ctx.reply(embed=embed, mention_author=True)
					await asyncio.sleep(15)
					await temp.delete()
					await ctx.message.delete()
				else:
					pass
			if "Spotify" not in str(member.activities):
				ctx.command.reset_cooldown(ctx)
				embed = discord.Embed(title="Error", description="That user is not listening to Spotify at the moment you silly goose.", color=Color.red())
				temp = await ctx.reply(embed=embed, mention_author=True)
				await asyncio.sleep(15)
				await temp.delete()
				await ctx.message.delete()
		except Exception as exc:
			tragedy.logError(exc)

	@commands.command()
	@commands.cooldown(1, 5, type=BucketType.member)
	async def weather(self, ctx, *, location: str=None):
		if location is None:
			ctx.command.reset_cooldown(ctx)
			pass
		else:
			try:
				x = location.lower()
				async with self.aiohttp.get('http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}'.format(x, "ab7f918b6ac57bfbcb45607f320907e1")) as x:
					parse = await x.json()
					cord1, cord2 = str(parse['coord']['lon']), str(parse['coord']['lat'])
					embed=discord.Embed(title='{} ({})'.format(parse['name'], parse['sys']['country']), colour=discord.Color.green(), description='Longitude : {} | Latitude : {}'.format(cord1, cord2))
					embed.set_thumbnail(url="https://www.countryflags.io/{}/flat/64.png".format(parse['sys']['country']))
					embed.add_field(name='Wind Speed', value=str(parse['wind']['speed']) + " MPH", inline=False)
					embed.add_field(name='Humidity Percentage', value=str(parse['main']['humidity']) + '%', inline=False)
					embed.add_field(name='Weather', value=parse['weather'][0]['main'] + " ({})".format(parse['weather'][0]['description']))
					embed.add_field(name='Clouds', value=str(parse['clouds']['all']), inline=False)
					embed.add_field(name='Temperature', value=str(round(parse['main']['temp'] * 1.8 - 459.67)) + ' °F')
					embed.add_field(name='Feels Like', value=str(round(parse['main']['feels_like'] * 1.8 - 459.67)) + ' °F')
					embed.add_field(name="Time Zone", value=str(parse['timezone']), inline=False)
					embed.add_field(name="Min Temperature", value=str(round(parse['main']['temp_min'] * 1.8 - 459.67)) + ' °F')
					embed.add_field(name="Max Temperature", value=str(round(parse['main']['temp_max'] * 1.8 - 459.67)) + ' °F')
					await ctx.reply(embed=embed, mention_author=True)
			except KeyError as exc:
				tragedy.logError(exc)
				await ctx.send('that aint even a place bro bro :thinking:')
				pass
				
	@commands.command()
	@commands.cooldown(1, 5, BucketType.member)
	async def fees(self, ctx):
		async with self.aiohttp.get("https://mempool.space/api/v1/fees/recommended") as response:
			parse = await response.json()
			embed = discord.Embed(title="BTC Fees", description="The [mempool.space](https://mempool.space) Recommended BTC Fees", color=Color.green())
			embed.add_field(name="Fastest", value=parse["fastestFee"], inline=False)
			embed.add_field(name="Half Hour", value=parse["halfHourFee"], inline=False)
			embed.add_field(name="Hour", value=parse["hourFee"], inline=False)
			await ctx.reply(embed=embed, mention_author=True)

	@commands.command(aliases=["crypto", "price", "cryptos"])
	@commands.cooldown(1, 5, BucketType.member)
	async def prices(self, ctx):
		async with self.aiohttp.get("https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD,EUR,CAD") as BTC:
			async with self.aiohttp.get("https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD,EUR,CAD") as ETH:
				async with self.aiohttp.get("https://min-api.cryptocompare.com/data/price?fsym=XMR&tsyms=USD,EUR,CAD") as XMR:
					jObjBTC = await BTC.json()
					jObjETH = await ETH.json()
					jObjXMR = await XMR.json()
					embed = discord.Embed(title="Crypto Currency Prices", color=discord.Color.green())
					embed.add_field(name="Bitcoin (BTC)", value="USD - **${}**\nEUR - **{}€**\nCAD - **${}**".format(jObjBTC['USD'], jObjBTC['EUR'], jObjBTC['CAD']), inline=False)
					embed.add_field(name="Ethereum (ETH)", value="USD - **${}**\nEUR - **{}€**\nCAD - **${}**".format(jObjETH['USD'], jObjETH['EUR'], jObjETH['CAD']), inline=False)
					embed.add_field(name="Monero (XMR)", value="USD - **${}**\nEUR - **{}€**\nCAD - **${}**".format(jObjXMR['USD'], jObjXMR['EUR'], jObjXMR['CAD']), inline=False)
					await ctx.reply(embed=embed, mention_author=True)

def setup(bot):
	bot.add_cog(Info(bot))