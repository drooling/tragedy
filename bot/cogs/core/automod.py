# -*- coding: utf-8 -*-

import ast
import contextlib
import pickle
import pprint
import re

import aiohttp
import bot.utils.utilities as tragedy
import discord
import pymysql.cursors
from bot.utils.classes import AutoModConfig
from discord.colour import Color
from discord.ext import commands, tasks
from profanity_filter import ProfanityFilter


class Automod(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.aiohttp = aiohttp.ClientSession()
        self.profanity = ProfanityFilter(languages=['en', 'es', 'de', 'fr'])
        self.domains: list = ["top.gg/", "discord.gg/",
                              ".gg/", "discord.io/", "dsc.gg/"]
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
        self.AutoModTypesNONE = AutoModConfig(profanity_filter=False, link_filter=False,
                                              mention_filter=False, mention_length=0, spam_filter=False, spam_ratio=(0, 0))
        self.AutoModTypesLOW = AutoModConfig(profanity_filter=False, link_filter=False,
                                             mention_filter=True, mention_length=8, spam_filter=True, spam_ratio=(5, 3))
        self.AutoModTypesMEDIUM = AutoModConfig(
            profanity_filter=True, link_filter=True, mention_filter=True, mention_length=6, spam_filter=True, spam_ratio=(5, 3))
        self.AutoModTypesHIGH = AutoModConfig(
            profanity_filter=True, link_filter=True,  mention_filter=True, mention_length=3, spam_filter=True, spam_ratio=(5, 3))

    async def get_config(self, ctx: commands.Context) -> AutoModConfig:
        with self.pool.cursor() as cursor:
            cursor: pymysql.cursors.Cursor = cursor
            cursor.execute(
                "SELECT config FROM `auto-mod` WHERE guild=%s", (ctx.guild.id))
            row: dict = cursor.fetchone()
            return pickle.loads(row.get("config"), encoding="utf-8") or None

    @tasks.loop(seconds=35)
    async def mysqlPing(self):
        connected = bool(self.pool.open)
        pprint.pprint(
            "Testing connection to mysql database () --> {}".format(str(connected).upper()))
        if connected is False:
            self.pool.ping(reconnect=True)
            pprint.pprint("Reconnecting to database () --> SUCCESS")
        else:
            pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        with contextlib.suppress(Exception):
            if message.guild.id == 769727903419990037:
                if bool(re.findall(discord.utils._URL_REGEX, message.clean_content)):
                    await self.rickroll_filter(message)
                if bool(message.raw_mentions):
                    await self.mention_filter(message, 3)

    async def link_filter(self, message: discord.Message):
        if any(domain in str(message.content).lower() for domain in self.domains):
            await message.delete()
            await message.channel.send(embed=discord.Embed(
                title="Tragedy Auto-mod",
                description="Invite links are not allowed in this server",
                color=Color.red()
            ))
        else:
            return

    async def mention_filter(self, message: discord.Message, max_mentions: int):
        if len(message.raw_mentions) >= max_mentions:
            if not message.author.guild_permissions.administrator:
                await message.delete()
                await message.channel.send(embed=discord.Embed(
                    title="Tragedy Auto-mod",
                    description="You cannot mention more than %s members at a time" % (
                        str(max_mentions)),
                    color=Color.red()
                ))
            else:
                return
        else:
            return

    async def rickroll_filter(self, message: discord.Message):
        rick_emojis = ['\U0001F1F7', '\U0001F1EE', '\U0001F1E8', '\U0001F1F0']
        phrases = ["rickroll", "rick roll",
                   "rick astley", "never gonna give you up"]
        source = str(await (await self.aiohttp.get(re.findall(pattern=discord.utils._URL_REGEX, string=message.content, flags=re.MULTILINE | re.IGNORECASE)[0], allow_redirects=True)).content.read()).lower()
        rickRoll = bool(
            (re.findall('|'.join(phrases), source, re.MULTILINE | re.IGNORECASE)))
        if rickRoll:
            [await message.add_reaction(emoji) for emoji in rick_emojis]
        else:
            return

    async def profanity_filter(self, message: discord.Message):
        content: str = message.clean_content
        clean: bool = bool(self.profanity.is_clean(content))
        if not clean:
            await message.delete()
            embed = discord.Embed(
                description="You cannot use profane language in this server.",
                color=Color.red()
            )
            embed.set_author(name=message.author,
                             icon_url=message.author.avatar_url)
            embed.add_field(name="Orginal Profanity",
                            value='||%s||' % (content))
            embed.add_field(name="Clean Alternative", value='`%s`' %
                            (self.profanity.censor(content)))
            await message.channel.send(embed=embed)
        else:
            return

    @commands.command()
    async def test(self, ctx):
        print(await self.get_config(ctx))


def setup(bot):
    bot.add_cog(Automod(bot))
