# -*- coding: utf-8 -*-

import contextlib
from datetime import datetime
import typing

import aiohttp
import subprocess
import shlex
import io
import re
import dateutil.parser
import discord
import humanize
from discord.activity import *
from bot.utils.imageEmbed import FileType, ImageEmbed
from discord.colour import Color
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import bot.utils.utilities as tragedy
from bot.utils.paginator import Paginator


class Info(commands.Cog, description="Commands that return information"):
    def __init__(self, bot):
        self.bot = bot
        self.aiohttp = aiohttp.ClientSession()

    @commands.command(description="you know what this does dont play stupid", help="whois [member]")
    @commands.cooldown(1, 5, type=BucketType.member)
    async def whois(self, ctx, member: commands.MemberConverter = None):
        member = member if member != None else ctx.author
        roleNameList = list(
            role.mention for role in member.roles if role != ctx.guild.default_role)
        # userProfile = await self.bot.fetch_user_profile(member.id) User profile has been depracated since v1.7
        # externalAccounts = list("Type: {} - Username: {}".format(external.get("type", "Error"), external.get("name", "Error")) for external in await userProfile.connected_accounts) User profile has been depracated since v1.7
        embed = discord.Embed(color=Color.green(), timestamp=datetime.utcnow())
        embed.set_author(name="{} ({})".format(
            member, member.id), icon_url=member.avatar_url)
        embed.add_field(name="Basic Info",
                        value="Joined Server At - **{} (Around {})**\nRegistered on Discord At - **{} (Around {})**".format(
                            humanize.naturaldate(member.joined_at),
                            humanize.naturaltime(
                                datetime.now() - member.joined_at),
                            humanize.naturaldate(member.created_at),
                            humanize.naturaltime(datetime.now() - member.created_at)))
        embed.add_field(name="Status Info (Buggy)",
                        value="Desktop Status - **{}**\nMobile Status - **{}**\nWeb Application Status - **{}**".format(
                            tragedy.HumanStatus(str(member.desktop_status)),
                            tragedy.HumanStatus(str(member.mobile_status)),
                            tragedy.HumanStatus(str(member.web_status))), inline=False)
        embed.add_field(name="Role Info", value="Top Role - {}\nRole(s) - {}".format(
            member.top_role.mention if member.top_role != ctx.guild.default_role else "None",
            ', '.join(roleNameList).removesuffix(', ') if roleNameList != [] else "None"), inline=False)
        embed.add_field(name="Flags",
                        value="{} - Discord Staff\n{} - Discord Partner\n{} - Verified Bot Developer".format(
                            tragedy.EmojiBool(member.public_flags.staff),
                            tragedy.EmojiBool(member.public_flags.partner),
                            tragedy.EmojiBool(member.public_flags.verified_bot_developer)))
        # embed.add_field(name="Other Info", value="HypeSquad House - {}\nUser has Nitro - {}\nConnected Accounts - {}".format(str(userProfile.hypesquad_houses).title(), tragedy.EmojiBool(await userProfile.nitro), ', '.join(externalAccounts).removeprefix(', ') if externalAccounts != [] else "None")) User profile has been depracated since v1.7
        embed.set_footer(icon_url=ctx.author.avatar_url,
                         text='Requested By: {}'.format(ctx.author.name))
        await ctx.reply(embed=embed, mention_author=True)

    @commands.command(aliases=["guild", "si", "serverinfo", "guildinfo"],
                      description="Returns info about current guild", help="serverinfo")
    @commands.cooldown(1, 5, type=BucketType.member)
    async def server(self, ctx):
        findbots = sum(1 for member in ctx.guild.members if member.bot)
        vanity = "VANITY_URL" in str(ctx.guild.features)
        splash = "INVITE_SPLASH" in str(ctx.guild.features)
        animicon = "ANIMATED_ICON" in str(ctx.guild.features)
        discoverable = "DISCOVERY" in str(ctx.guild.features)
        banner = "BANNER" in str(ctx.guild.features)
        vanityFeature = "{} - Vanity URL".format(
            tragedy.EmojiBool(vanity)) if not vanity else "{} - Vanity URL ({})".format(vanity,
                                                                                        await ctx.guild.vanity_url)
        embed = discord.Embed(title='**{}**'.format(ctx.guild.name),
                              colour=Color.green(), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=str(ctx.guild.icon_url))
        embed.add_field(name="Members",
                        value="Bots: **{}**\nHumans: **{}**\nOnline Members: **{}/{}**".format(str(findbots),
                                                                                               ctx.guild.member_count - findbots,
                                                                                               sum(
                            member.status != discord.Status.offline and not member.bot
                            for member in
                            ctx.guild.members),
                            str(ctx.guild.member_count)))
        embed.add_field(name="Channels",
                        value="\U0001f4ac Text Channels: **{}**\n\U0001f50a Voice Channels: **{}**".format(
                            len(ctx.guild.text_channels), len(ctx.guild.voice_channels)))
        embed.add_field(name="Important Info",
                        value="Owner: {}\nVerification Level: **{}**\nGuild ID: **{}**".format(ctx.guild.owner.mention,
                                                                                               str(ctx.guild.verification_level).title(
                                                                                               ),
                                                                                               ctx.guild.id),
                        inline=False)
        embed.add_field(name="Other Info",
                        value="AFK Channel: **{}**\n AFK Timeout: **{} minute(s)**\nCustom Emojis: **{}**\nRole Count: **{}**\nFilesize Limit - **{}**".format(
                            ctx.guild.afk_channel, str(
                                ctx.guild.afk_timeout / 60), len(ctx.guild.emojis),
                            len(ctx.guild.roles), humanize.naturalsize(ctx.guild.filesize_limit)), inline=False)
        embed.add_field(name="Server Features",
                        value="{} - Banner\n{}\n{} - Splash Invite\n{} - Animated Icon\n{} - Server Discoverable".format(
                            tragedy.EmojiBool(
                                banner), vanityFeature, tragedy.EmojiBool(splash),
                            tragedy.EmojiBool(animicon), tragedy.EmojiBool(discoverable)))
        embed.add_field(name="Boost Info",
                        value="Number of Boosts - **{}**\nBooster Role - **{}**\nBoost Level/Tier - **{}**".format(
                            str(ctx.guild.premium_subscription_count),
                            ctx.guild.premium_subscriber_role.mention if ctx.guild.premium_subscriber_role != None else ctx.guild.premium_subscriber_role,
                            ctx.guild.premium_tier))
        await ctx.reply(embed=embed, mention_author=True)

    @commands.command(name="emoji", aliases=["ei", "emojinfo"], description="Returns info about specified emoji",
                      help="emoji <emoji>")
    @commands.cooldown(1, 5, type=BucketType.member)
    async def _emoji(self, ctx, emoji: commands.EmojiConverter):
        embed = discord.Embed(title='**{}**'.format(emoji.name),
                              colour=Color.green(), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=str(emoji.url))
        embed.add_field(name="Basic Info",
                        value="Emoji Name - **{}**\nEmoji ID - **{}**\nCreated At - **{} ({})**".format(emoji.name,
                                                                                                        emoji.id,
                                                                                                        humanize.naturaldate(
                                                                                                            emoji.created_at),
                                                                                                        humanize.naturaltime(
                                                                                                            datetime.now() - emoji.created_at)))
        embed.add_field(name="Guild Info",
                        value="Guild Name - **{}**\nGuild ID - **{}**".format(emoji.guild.name, emoji.guild_id))
        embed.add_field(name="Features",
                        value="Animated - {}\nAvailable - {}\nManaged by Twitch - {}\nRequires Colons - {}".format(
                            tragedy.EmojiBool(emoji.animated), tragedy.EmojiBool(
                                emoji.available),
                            tragedy.EmojiBool(emoji.managed), tragedy.EmojiBool(emoji.require_colons)), inline=False)
        await ctx.reply(embed=embed, mention_author=True)

    @commands.command(name="role", aliases=['ri', 'roleinfo'], description="Returns info about specified role",
                      help="role <role>")
    @commands.cooldown(1, 5, BucketType.member)
    async def _role(self, ctx: commands.Context, role: commands.RoleConverter):
        async with ctx.typing():
            embed = discord.Embed(title=role.name, color=role.color)
            embed.add_field(name="Basic Info",
                            value="Role Name - **{}**\nRole ID - **{}**\nCreated At - **{} ({})**".format(role.name,
                                                                                                          role.id,
                                                                                                          humanize.naturaldate(
                                                                                                              role.created_at),
                                                                                                          humanize.naturaltime(
                                                                                                              datetime.now() - role.created_at)))

            embed.add_field(name="Features",
                            value="Mentionable - {}\nBot Role - {}\nManaged by Integration - {}\nBooster Role - {}\nDefault Role - {}".format(
                                tragedy.EmojiBool(role.mentionable), tragedy.EmojiBool(
                                    role.is_bot_managed()),
                                tragedy.EmojiBool(role.managed), tragedy.EmojiBool(
                                    role.is_premium_subscriber()),
                                tragedy.EmojiBool(role.is_bot_managed())), inline=False)
            await ctx.reply(embed=embed, mention_author=True)

    @commands.command(aliases=['pfp', 'avatar'], description="you know what this does too", help="av [member]")
    @commands.cooldown(1, 5, type=BucketType.member)
    async def av(self, ctx, member: commands.MemberConverter = None):
        member = member if member != None else ctx.author
        _128 = member.avatar_url_as(format='png', size=128)
        _256 = member.avatar_url_as(format='png', size=256)
        _512 = member.avatar_url_as(format='png', size=512)
        _1024 = member.avatar_url_as(format='png', size=1024)
        _2048 = member.avatar_url_as(format='png', size=2048)
        embed = discord.Embed(color=Color.green(),
                              description="**[ [128]({}) ] - [ [256]({}) ] - [ 512 ] - [ [1024]({}) ] - [ [2048]({}) ]**".format(
            _128, _256, _1024, _2048))
        embed.set_image(url=_512)
        embed.set_footer(text="{}'s Avatar (512 x 512)".format(member))
        await ctx.reply(embed=embed, mention_author=True)

    @commands.command(description="Returns specified member's status(es)", help="status [member]")
    @commands.cooldown(1, 5, type=BucketType.member)
    async def status(self, ctx, member: commands.MemberConverter = None):
        target = member if member != None else ctx.author
        embeds = list()
        with contextlib.suppress(Exception):
            for activity in target.activities:
                if isinstance(activity, Spotify):
                    embedSpotify = discord.Embed(
                        title="Spotify", color=activity.color)
                    embedSpotify.url = "https://open.spotify.com/track/{}".format(
                        activity.track_id)
                    embedSpotify.set_author(name=target,
                                            icon_url="https://discord.com/assets/f0655521c19c08c4ea4e508044ec7d8c.png")
                    embedSpotify.set_thumbnail(url=activity.album_cover_url)
                    embedSpotify.add_field(
                        name="Song Title", value=activity.title)
                    embedSpotify.add_field(
                        name="Song Album", value=activity.album)
                    embedSpotify.add_field(name="Song Artist(s)", value=', '.join(activity.artists).removeprefix(', '),
                                           inline=False)
                    embedSpotify.add_field(name="Song Length",
                                           value=dateutil.parser.parse(str(activity.duration)).strftime('%M:%S'))
                    embeds.append(embedSpotify)
                if isinstance(activity, CustomActivity):
                    if activity.name is not None and activity.emoji is not None and activity.emoji.is_custom_emoji() is True:
                        description = (
                            "```<a:{}:{}> {}```".format(activity.emoji.name, activity.emoji.id, activity.name))
                    elif activity.name is not None and activity.emoji is not None:
                        description = ("```{} {}```".format(
                            activity.emoji, activity.name))
                    elif activity.emoji is not None and activity.name is None:
                        description = ("```{}```".format(activity.emoji))
                    elif activity.name is not None and activity.emoji is None:
                        description = ("```{}```".format(activity.name))
                    embedCustom = discord.Embed(title="{}#{} Custom Status".format(target.name, target.discriminator),
                                                color=Color.green(), description=description)
                    embeds.append(embedCustom)
                if isinstance(activity, Game):
                    embedGame = discord.Embed(
                        title=target, color=Color.green())
                    embedGame.add_field(name="Playing", value=activity.name)
                    embeds.append(embedGame)
                if isinstance(activity, Streaming):
                    embedStream = discord.Embed(title="Streaming on [{}]({})".format(activity.platform, activity.url),
                                                color=Color.green())
                    embedStream.add_field(name="Playing", value=activity.game)
                    embedStream.add_field(
                        name="Details", value=activity.details)
                    if activity.platform == "Twitch":
                        embedStream.add_field(name="Twitch Profile",
                                              value="https://www.twitch.tv/{}".format(activity.twitch_name))
                    embeds.append(embedStream)
                else:
                    pass
            paginate = Paginator(self.bot, ctx, embeds)
            await paginate.run() if len(embeds) > 1 else await ctx.send(embed=embeds[0]) if len(
                embeds) > 0 else await ctx.send("they aint doin nun you silly goose")

    @commands.command(description="Returns weather in specified place", help="weather <location>")
    @commands.cooldown(1, 5, type=BucketType.member)
    async def weather(self, ctx, *, location: typing.Optional[str] = None):
        if location is None:
            ctx.command.reset_cooldown(ctx)
            pass
        else:
            try:
                x = location.lower()
                async with self.aiohttp.get('http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}'.format(x,
                                                                                                                  tragedy.DotenvVar(
                                                                                                                      "weathermapApiKey"))) as x:
                    parse = await x.json()
                    cord1, cord2 = str(parse['coord']['lon']), str(
                        parse['coord']['lat'])
                    embed = discord.Embed(title='{} ({})'.format(parse['name'], parse['sys']['country']),
                                          colour=discord.Color.green(),
                                          description='Longitude : {} | Latitude : {}'.format(cord1, cord2))
                    embed.set_thumbnail(
                        url="https://www.countryflags.io/{}/flat/64.png".format(parse['sys']['country']))
                    embed.add_field(name='Wind Speed', value=str(
                        parse['wind']['speed']) + " MPH", inline=False)
                    embed.add_field(name='Humidity Percentage', value=str(parse['main']['humidity']) + '%',
                                    inline=False)
                    embed.add_field(name='Weather', value=parse['weather'][0]['main'] + " ({})".format(
                        parse['weather'][0]['description']))
                    embed.add_field(name='Clouds', value=str(
                        parse['clouds']['all']), inline=False)
                    embed.add_field(name='Temperature', value=str(
                        round(parse['main']['temp'] * 1.8 - 459.67)) + ' °F')
                    embed.add_field(name='Feels Like',
                                    value=str(round(parse['main']['feels_like'] * 1.8 - 459.67)) + ' °F')
                    embed.add_field(name="Time Zone", value=str(
                        parse['timezone']), inline=False)
                    embed.add_field(name="Min Temperature",
                                    value=str(round(parse['main']['temp_min'] * 1.8 - 459.67)) + ' °F')
                    embed.add_field(name="Max Temperature",
                                    value=str(round(parse['main']['temp_max'] * 1.8 - 459.67)) + ' °F')
                    await ctx.reply(embed=embed, mention_author=True)
            except KeyError as exc:
                tragedy.logError(exc)
                await ctx.send('that aint even a place bro bro :thinking:\nor you typed it wrong')
                pass

    @commands.command(description="Returns recommended bitcoin fees", help="fees")
    @commands.cooldown(1, 5, BucketType.member)
    async def fees(self, ctx):
        async with self.aiohttp.get("https://mempool.space/api/v1/fees/recommended") as response:
            parse = await response.json()
            embed = discord.Embed(title="BTC Fees",
                                  description="The [mempool.space](https://mempool.space) Recommended BTC Fees",
                                  color=Color.green())
            embed.add_field(
                name="Fastest", value=parse["fastestFee"], inline=False)
            embed.add_field(name="Half Hour",
                            value=parse["halfHourFee"], inline=False)
            embed.add_field(name="Hour", value=parse["hourFee"], inline=False)
            await ctx.reply(embed=embed, mention_author=True)

    @commands.command(aliases=["crypto", "price", "cryptos"], description="Returns current price of BTC, ETH, and XMR",
                      help="prices")
    @commands.cooldown(1, 5, BucketType.member)
    async def prices(self, ctx):
        async with self.aiohttp.get("https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD,EUR,CAD") as BTC:
            async with self.aiohttp.get(
                    "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD,EUR,CAD") as ETH:
                async with self.aiohttp.get(
                        "https://min-api.cryptocompare.com/data/price?fsym=XMR&tsyms=USD,EUR,CAD") as XMR:
                    jObjBTC = await BTC.json()
                    jObjETH = await ETH.json()
                    jObjXMR = await XMR.json()
                    embed = discord.Embed(
                        title="Crypto Currency Prices", color=discord.Color.green())
                    embed.add_field(name="Bitcoin (BTC)",
                                    value="USD - **${}**\nEUR - **{}€**\nCAD - **${}**".format(jObjBTC['USD'],
                                                                                               jObjBTC['EUR'],
                                                                                               jObjBTC['CAD']),
                                    inline=False)
                    embed.add_field(name="Ethereum (ETH)",
                                    value="USD - **${}**\nEUR - **{}€**\nCAD - **${}**".format(jObjETH['USD'],
                                                                                               jObjETH['EUR'],
                                                                                               jObjETH['CAD']),
                                    inline=False)
                    embed.add_field(name="Monero (XMR)",
                                    value="USD - **${}**\nEUR - **{}€**\nCAD - **${}**".format(jObjXMR['USD'],
                                                                                               jObjXMR['EUR'],
                                                                                               jObjXMR['CAD']),
                                    inline=False)
                    await ctx.reply(embed=embed, mention_author=True)

    @commands.command(name="btcbal", description="Gets specified BTC wallet's balance", help="bal <wallet>")
    async def _bal(self, ctx: commands.Context, *, wallet: str):
        async with self.aiohttp.get(
                "https://chain.so/api/v2/get_address_balance/BTC/{}/500".format(wallet)) as response:
            json = await response.json()
            if json["status"] == "fail":
                await ctx.reply(embed=discord.Embed(
                    title="Oops !",
                    description="Invalid BTC wallet address",
                    color=Color.red()
                ), mention_author=True)
            else:
                await ctx.reply(embed=discord.Embed(
                    title=wallet,
                    description="```{}```".format(
                                json["data"]["confirmed_balance"]),
                    color=Color.green()
                ), mention_author=True)

    @commands.command(name="tx", description="Gets information about specified BTC transaction ID",
                      help="tx <transaction>")
    async def _tx(self, ctx: commands.Context, *, transaction: str):
        async with self.aiohttp.get("https://chain.so/api/v2/get_tx/BTC/{}".format(transaction)) as response:
            json = await response.json()
            if json["status"] == "fail":
                await ctx.reply(embed=discord.Embed(
                    title="Oops !",
                    description="Invalid BTC transaction",
                    color=Color.red()
                ), mention_author=True)
            else:
                embed = discord.Embed(
                    title=transaction,
                    color=Color.green()
                )
                inputs = list()
                outputs = list()
                for _index in json["data"]["inputs"]:
                    inputs.append(
                        str(_index["address"] + ' - ' + _index["value"]))
                for _index in json["data"]["outputs"]:
                    outputs.append(
                        str(_index["address"] + ' - ' + _index["value"]))
                embed.add_field(name="Confirmations",
                                value=json["data"]["confirmations"])
                embed.add_field(name="Network Fee",
                                value=json["data"]["network_fee"])
                embed.add_field(name="Date", value=humanize.naturaldate(
                    datetime.fromtimestamp(json["data"]["time"])))
                embed.add_field(name="Output Wallets (Address - Value)",
                                value='\n'.join(outputs).strip(), inline=False)
                embed.add_field(name="Input Wallets (Address - Value)",
                                value='\n'.join(inputs).strip(), inline=False)
                await ctx.reply(embed=embed, mention_author=True)

    @commands.command(name="covid", description="Returns worldwide covid statistics", help="covid")
    async def _covid(self, ctx: commands.Context):
        async with ctx.typing():
            async with self.aiohttp.get("https://disease.sh/v3/covid-19/all") as jsonResponse:
                embed = discord.Embed(
                    title="Covid-19 Statistics", color=Color.green())
                embed.set_thumbnail(
                    url="https://www.lynchowens.com/images/blog/Coronavirus-illustration.png")
                json = await jsonResponse.json()
                embed.add_field(name="Cases",
                                value="Total Cases - **{}**\nCases Today - **{}**\nCases Per 1 Million People - **{}**".format(
                                    humanize.intword(json["cases"]), humanize.intword(
                                        json["todayCases"]),
                                    humanize.intword(json["casesPerOneMillion"])))
                embed.add_field(name="Deaths",
                                value="Total Deaths - **{}**\nDeaths Today - **{}**\nDeaths Per 1 Million People - **{}**".format(
                                    humanize.intword(json["deaths"]), humanize.intword(
                                        json["todayDeaths"]),
                                    humanize.intword(json["deathsPerOneMillion"])), inline=False)
                embed.add_field(name="Recovered",
                                value="Total Recovered - **{}**\nRecovered Today - **{}**\nRecovered Per 1 Million People - **{}**".format(
                                    humanize.intword(json["recovered"]), humanize.intword(
                                        json["todayRecovered"]),
                                    humanize.intword(json["recoveredPerOneMillion"])))
                embed.add_field(name="Tests", value="Total Tests - **{}**\nTests Per 1 Million People - **{}**".format(
                    humanize.intword(json["tests"]), humanize.intword(json["testsPerOneMillion"])), inline=False)
                await ctx.reply(embed=embed, mention_author=True)

    @commands.command(aliases=["pypi"])
    async def pypisearch(self, ctx, arg: str):
        res_raw = await self.aiohttp.get(f"https://pypi.org/pypi/{arg}/json")
        try:
            res_json = await res_raw.json()
        except aiohttp.ContentTypeError:
            return await ctx.send(
                embed=discord.Embed(
                    description="No such package found on [pypi.org](https://pypi.org).",
                    color=Color.red(),
                )
            )
        res = res_json["info"]

        def getval(key):
            return res[key] or "Unknown"

        name = getval("name")
        author = getval("author")
        author_email = getval("author_email")
        description = getval("summary")
        home_page = getval("home_page")
        project_url = getval("project_url")
        version = getval("version")
        _license = getval("license")
        embed = discord.Embed(
            title=name, description=description, color=Color.green()
        )
        embed.add_field(name="Author", value=author, inline=True)
        embed.add_field(name="Author Email", value=author_email, inline=True)
        embed.add_field(name="Version", value=version, inline=False)
        embed.add_field(name="License", value=_license, inline=True)
        embed.add_field(name="Project Url", value=project_url, inline=False)
        embed.add_field(name="Home Page", value=home_page)
        embed.set_thumbnail(url="https://i.imgur.com/syDydkb.png")
        await ctx.send(embed=embed)

    @commands.command(aliases=['ss'])
    @commands.is_nsfw()
    async def screenshot(self, ctx: commands.Context, *, url: str):
        url = url.strip('<>')
        if not re.match(discord.utils._URL_REGEX, url):
            raise commands.BadArgument(
                'That is not a valid url. Try again with a valid one.')
        res = await self.aiohttp.get(f'https://image.thum.io/get/{url}')
        byt = io.BytesIO(await res.read())

        await ctx.send(embed=ImageEmbed.make("Screenshot", FileType.PNG), file=discord.File(byt, filename=f'linktr.ee_incriminating.png'))

    @commands.command(description="Finds accounts with specified username on various websites", help="investigo <username>")
    async def investigo(self, ctx, *, username: str):
        sanitized = shlex.quote(username)
        with contextlib.suppress(Exception):
            async with ctx.typing():
                output = subprocess.run(["bot\\assets\\executables\\Investigo\\Investigo.exe", "--database",
                                        "bot\\assets\\executables\\Investigo\\data.json", sanitized], stdout=subprocess.PIPE, timeout=35)
                list: str
                lastline = output.stdout.decode("utf-8")[:4035].splitlines()[-1]
                if len(lastline) < 15:
                    list = output.stdout.decode("utf-8")[:4035][:4035 - len(lastline)]
                else:
                    list = list = output.stdout.decode("utf-8")[:4035]
                await ctx.send(embed=discord.Embed(
                    title=sanitized,
                    description=list,
                    color=Color.green()
                ).set_footer(text="Username is sanitized don't even try os cmd injection"))


def setup(bot):
    bot.add_cog(Info(bot))
