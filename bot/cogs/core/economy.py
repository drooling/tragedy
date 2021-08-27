import ast
import math
import random
import pprint
import typing
import humanize
import pymysql.cursors

import bot.utils.utilities as tragedy
from bot.utils.paginator import Paginator
from bot.utils.classes import ShopItem

import discord
from discord.ext import commands, tasks
from discord.colour import Color
from discord.ext.commands.cooldowns import BucketType


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

		self.shop = {
			"fishingpole": ShopItem(item_name="Fishing Pole", item_price=35, item_emoji="\U0001F3A3"),
			"laptop": ShopItem(item_name="Laptop", item_price=750, item_emoji="\U0001F4BB"),
			"phone": ShopItem(item_name="Phone", item_price=500, item_emoji="\U0001F4F1")
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
				cursor.execute("UPDATE `economy` SET balance = balance + %s WHERE guild=%s AND user=%s", (amount, guild_id, user_id))
				return amount
			except AttributeError:
				cursor.execute("INSERT INTO `economy` (guild, user, balance) VALUES (%s, %s, %s)", (guild_id, user_id, amount))
				return amount

	async def buy_item(self, guild_id: int, user_id: int, item: str, amount: typing.Optional[int] = 1):
		item = item.casefold()
		price: int = (self.shop.get(item).price * amount)
		balance: int = await self.get_user_balance(guild_id, user_id)
		count: int = (await self.get_user_items(guild_id, user_id)).get(item) or 0

		if price < balance:
			with self.pool.cursor() as cursor:
				try:
					cursor.execute("UPDATE `economy` SET balance = balance - %s, items = JSON_SET(items, %s, %s + %s) WHERE guild = %s AND user = %s", (price, ("$." + item), count, amount, guild_id, user_id))
					return True
				except AttributeError:
					pass
		else:
			return False
	
	@commands.command()
	@commands.cooldown(1, 3, BucketType.member)
	async def bal(self, ctx: commands.Context, *, member: typing.Optional[commands.MemberConverter]):
		member = ctx.author if member is None else member
		balance = await self.get_user_balance(ctx.guild.id, member.id)
		embed = discord.Embed(title="%s's Financial Funds $$" % (member.name), color=Color.green(), description="**Wallet**: \U0001FA99 %s" % (humanize.intcomma(balance)))
		await ctx.send(embed=embed)

	@commands.command()
	@commands.cooldown(1, 5, BucketType.member)
	async def inv(self, ctx: commands.Context):
		inventory = await self.get_user_items(ctx.guild.id, ctx.author.id)
		full_inventory: str = str()
		for key in inventory.keys():
			key: str = key
			item: ShopItem = self.shop.get(key)

			full_inventory += "%s **%s**: `%s`\n" % (item.emoji, item.name, inventory.get(key))
		if full_inventory == str():
			full_inventory += "You own nothing"
		embed = discord.Embed(title="Your personal belongings", color=Color.green(), description=full_inventory)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	@commands.cooldown(1, 35, BucketType.member)
	async def beg(self, ctx: commands.Context):
		money = random.randrange(10, 125)
		await self.add_user_balance(ctx.guild.id, ctx.author.id, money)
		embed = discord.Embed(title="Imagine begging lol", color=Color.green(), description="You came by a very generous soul who gave you \U0001FA99 **%s** !" % (str(money)))
		await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	@commands.cooldown(1, 7, BucketType.member)
	async def buy(self, ctx: commands.Context, item: str, amount: typing.Union[int, str] = 1):
		if isinstance(amount, str):
			if amount.casefold() not in ("max", "half"):
				return await ctx.send(embed=discord.Embed(
				title="Tragedy shop",
				color=Color.red(),
				description="That is not a valid amount ! The valid amount's are numbers and `max` or `half`"
			))
		if item.casefold() not in self.shop.keys():
			return await ctx.send(embed=discord.Embed(
				title="Tragedy shop",
				color=Color.red(),
				description="That is not an item ! Check the shop with `xv shop`"
			))
		price: int = self.shop.get(item.casefold()).price
		if await self.get_user_balance(ctx.guild.id, ctx.author.id) < (price * amount):
			return await ctx.send(embed=discord.Embed(
				title="Tragedy shop",
				color=Color.green(),
				description="You do not have the funds to buy that !"
			))
		if await self.buy_item(ctx.guild.id, ctx.author.id, item.casefold()):
			embed = discord.Embed(title="Tragedy shop", color=Color.green(), description="You just bought **%s** `%s` for \U0001FA99 **%s**" % (str(amount), item, self.shop.get(item.casefold()).price))
			await ctx.send(embed=embed)

	@commands.command()
	@commands.guild_only()
	@commands.cooldown(1, 7, BucketType.member)
	async def shop(self, ctx: commands.Context):
		shop: str = str()
		for item in self.shop:
			shop += "%s **%s** - `%s`\n" % (self.shop.get(item).emoji, item, self.shop.get(item).price)
		try:
			embed = discord.Embed(title="Tragedy shop", color=Color.green(), description=shop)
		except discord.errors.Forbidden:
			lastline = shop[:2000].splitlines()[-1]
			embeds: typing.List = [discord.Embed(title="Tragedy shop", color=Color.green(), description=shop[:2000][:-len(lastline)]), discord.Embed(title="Tragedy shop", color=Color.green(), description=shop[2000 + len(lastline):])]
			await Paginator(self.bot, ctx, embeds).run()
		await ctx.send(embed=embed)

def setup(bot: commands.Bot):
	bot.add_cog(Economy(bot))