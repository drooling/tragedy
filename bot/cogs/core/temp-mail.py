import asyncio
import io
import json

import bot.utils.utilities as tragedy
import discord
import pymysql.cursors
from discord.colour import Color
from discord.errors import InvalidArgument
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord_components import *


class TempMail(commands.Cog, description="Temporary email commands !"):
    def __init__(self, bot):
        self.bot = bot
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
        self.aiohttp = __import__('aiohttp').ClientSession()
        DiscordComponents(bot)

    @commands.group(ignore_extra=True, invoke_without_command=True, description="Temporary email", help="temp")
    @tragedy.is_voter_only()
    @commands.cooldown(1, 60, type=BucketType.member)
    async def temp(self, ctx):
        with self.pool.cursor() as cursor:
            cursor.execute(
                "SELECT email FROM `temp-emails` WHERE user=%s", (ctx.author.id)
            )
            row = cursor.fetchone()
        try:
            email = row.get('email')
        except AttributeError:
            embed = discord.Embed(title="Tragedy temporary email",
                                  description="You do not have a tragedy temporary email setup yet\n Use `temp new` to create one", color=Color.red())
            return await ctx.send(embed=embed)

        embed = discord.Embed(title="Tragedy temporary email",
                              description="Your temporary email is `%s`" % (email), color=Color.green())
        await ctx.send(embed=embed)

    @temp.command(description="Generates new temporary email", help="temp new")
    @commands.cooldown(1, 86400, BucketType.user)
    async def new(self, ctx):
        async with self.aiohttp.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox") as request:
            email = json.loads(await request.text())[0]
        with self.pool.cursor() as cursor:
            cursor.execute(
                "REPLACE INTO `temp-emails` SET user=%s, email=%s", (
                    ctx.author.id, email)
            )
        embed = discord.Embed(title="Tragedy temporary email",
                              description="Your new temporary email address is `%s`" % (email), color=Color.green())
        await ctx.send(embed=embed)

    @temp.group()
    async def inbox(self, ctx):
        pass

    @inbox.command(description="Gets emails from temporary email's inbox", help="temp inbox view")
    @commands.cooldown(1, 35, BucketType.user)
    async def view(self, ctx):
        def check(response):
            return ctx.author == response.user and response.channel == ctx.channel

        with self.pool.cursor() as cursor:
            cursor.execute(
                "SELECT email FROM `temp-emails` WHERE user=%s", (ctx.author.id)
            )
            row = cursor.fetchone()
        try:
            email = row.get('email')
        except AttributeError:
            embed = discord.Embed(title="Tragedy temporary email",
                                  description="You do not have a tragedy temporary email setup yet", color=Color.red())
            return await ctx.send(embed=embed)
        async with self.aiohttp.get("https://www.1secmail.com/api/v1/?action=getMessages&login=%s&domain=%s" % (
                email.split('@')[0], email.split('@')[1])) as request:
            jObj = await request.json()
            SelectOptions = []
            for _index in range(len(jObj)):
                SelectOptions.append(
                    SelectOption(label='%s (%s)' % (jObj[_index]['subject'], jObj[_index]['from']),
                                 value=jObj[_index]['id']))
            try:
                SelectMail = await ctx.send(content="Your emails", components=[
                    [
                        Select(
                            placeholder="Select the email you wish to view.",
                            max_values=1,
                            options=SelectOptions
                        )
                    ]
                ])
            except InvalidArgument:
                return await ctx.send(":x: **Your inbox is empty !**")
            try:
                selectInteraction = await self.bot.wait_for("select_option", check=check, timeout=45)
            except asyncio.exceptions.TimeoutError:
                return await SelectMail.edit(content="Took too long !", embed=None, components=[])
            async with self.aiohttp.get(
                "https://www.1secmail.com/api/v1/?action=readMessage&login=%s&domain=%s&id=%s" % (
                    email.split('@')[0], email.split('@')[1], selectInteraction.component[0].value)) as request:
                jObj = await request.json()
            embed = discord.Embed(title=jObj['subject'], color=Color.green())
            embed.add_field(name="From", value=jObj['from'])
            embed.add_field(name="Date", value=jObj['date'])
            if jObj['htmlBody'] == "":
                if len(jObj['textBody']) > 1500:
                    await ctx.send(file=discord.File(fp=io.BytesIO(str(jObj['textBody']).encode(errors='ignore')),
                                                     filename="email.txt"))
                else:
                    embed.add_field(name="Body", value="```" +
                                    jObj['textBody'] + "```", inline=False)
            else:
                if len(jObj['textBody']) > 1500:
                    await ctx.send(file=discord.File(fp=io.BytesIO(str(jObj['textBody']).encode(errors='ignore')),
                                                     filename="email.txt"))
                else:
                    embed.add_field(name="Body", value="```" +
                                    jObj['textBody'] + "```", inline=False)
                await SelectMail.delete()
                await ctx.message.add_reaction("✅")
                return await ctx.author.send(embed=embed, file=discord.File(
                    fp=io.BytesIO(str(jObj['htmlBody']).encode(errors='ignore')), filename="body.html"))
            await SelectMail.delete()
            await ctx.message.add_reaction("✅")
            await ctx.author.send(embed=embed)


def setup(bot):
    bot.add_cog(TempMail(bot))
