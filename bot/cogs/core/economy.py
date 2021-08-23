import ast
import random
import pprint
import pymysql.cursors

import bot.utils.utilities as tragedy

import discord
from discord.ext import commands, tasks
from discord.colour import Color


class Economy(commands.Cog, description="Economy system lol"):
    def __init__(self, bot: commands.Bot):
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
        self.mysqlPing.start()
        self.emojiKey = {
            "fishing pole": "\U0001F3A3",
            "laptop": "\U0001F4BB"
        }

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

    async def get_user_balance(self, guild_id: int, user_id: int):
        with self.pool.cursor() as cursor:
            try:
                cursor.execute("SELECT balance FROM `economy` WHERE guild=%s AND user=%s", (guild_id, user_id))
                row: dict = cursor.fetchone()
                return row.get('balance')
            except AttributeError:
                cursor.execute("INSERT INTO `economy` (guild, user) VALUES (%s, %s)", (guild_id, user_id))
                return 0

    async def get_user_items(self, guild_id: int, user_id: int):
        with self.pool.cursor() as cursor:
            try:
                cursor.execute("SELECT items FROM `economy` WHERE guild=%s AND user=%s", (guild_id, user_id))
                row: dict = cursor.fetchone()
                return ast.literal_eval(row.get('items'))
            except AttributeError:
                cursor.execute("INSERT INTO `economy` (guild, user) VALUES (%s, %s)", (guild_id, user_id))
                return {}

    async def add_user_balance(self, guild_id: int, user_id: int, amount: int):
        with self.pool.cursor() as cursor:
            try:
                cursor.execute("UPDATE `economy` SET balance = balance + {0} WHERE guild=%s AND user=%s".format(amount), (guild_id, user_id))
                return amount
            except AttributeError:
                cursor.execute("INSERT INTO `economy` (guild, user, balance) VALUES (%s, %s, %i)", (guild_id, user_id, amount))
                return amount
    
    @commands.command()
    async def bal(self, ctx: commands.Context):
        balance = await self.get_user_balance(ctx.guild.id, ctx.author.id)
        embed = discord.Embed(title="Your Financial Funds $$", color=Color.green(), description="**Wallet**: \U0001FA99 %s" % (str(balance)))
        await ctx.send(embed=embed)

    @commands.command()
    async def inv(self, ctx: commands.Context):
        inventory = await self.get_user_items(ctx.guild.id, ctx.author.id)
        full_inventory: str = str()
        for key in inventory.keys():
            full_inventory += "%s **%s**: `%s`\n" % (self.emojiKey.get(key), key.title(), inventory.get(key))
        embed = discord.Embed(title="Your personal belongings", color=Color.green(), description=full_inventory)
        await ctx.send(embed=embed)

    @commands.command()
    async def beg(self, ctx):
        money = random.randrange(10, 250)
        await self.add_user_balance(ctx.guild.id, ctx.author.id, money)
        embed = discord.Embed(title="Imagine begging lol", color=Color.green(), description="You came by a very generous soul who gave you \U0001FA99 **%s** !" % (str(money)))
        await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(Economy(bot))