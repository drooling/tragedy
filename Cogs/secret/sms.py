import json
import logging
import sys
import traceback
import discord
from discord.ext import commands
import pymysql.cursors
import resources.utilities as tragedy

databaseConfig = pymysql.connect(
	host=tragedy.dotenvVar("mysqlServer"),
	user="root",
	password=tragedy.dotenvVar("mysqlPassword"),
	port=3306,
	database="sms",
	charset='utf8mb4',
	cursorclass=pymysql.cursors.DictCursor,
	read_timeout=5,
	write_timeout=5,
	connect_timeout=5,
	autocommit=True
	)

cursor = databaseConfig.cursor()

class Sms(commands.Cog, command_attrs=dict(hidden=True)):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	def authorized():
		async def predicate(ctx):
			with open("./resources/authorized.json", "r") as list:
				return ctx.author.id in json.load(list)["auth"]
		return commands.check(predicate)

	@commands.group(pass_context=True, case_insensitive=True)
	@commands.is_owner()
	async def hwid(self, ctx: commands.Context):
		pass

	@hwid.command(pass_context=True, ignore_extra=True)
	@commands.is_owner()
	async def ban(self, ctx: commands.Context, *, hwid: str):
		try:
			cursor.execute("INSERT INTO banned (hwid) VALUES (%s)", (hwid.strip("',/\n")))
			databaseConfig.commit()
			embed = discord.Embed(title="HWID Ban ({})".format(hwid.strip("',/\n")), color=discord.Colour.green())
			embed.add_field(name="Status", value="Success", inline=False)
			await ctx.reply(embed=embed, mention_author=True)
			print("[Query] " + "[INSERT INTO banned (hwid) VALUES (%s)] was queried to database by %s.", (hwid.strip("',/\n"), ctx.author.name))
		except Exception as exc:
			exc_type, exc_value, exc_tb = sys.exc_info()
			exception = traceback.format_exception(exc_type, exc_value, exc_tb)
			logging.log(logging.ERROR, exception)
			embed = discord.Embed(title="HWID Ban ({})".format(hwid.strip("',/\n")), color=discord.Colour.red())
			embed.add_field(name="Error", value="Internal Server Error [\"  {}  \"]".format(exc), inline=False)
			await ctx.reply(embed=embed, mention_author=True)

	@hwid.command(pass_context=True, ignore_extra=True)
	@commands.is_owner()
	async def unban(self, ctx: commands.Context, *, hwid: str):
		try:
			cursor.execute("DELETE FROM banned WHERE hwid = %s", (hwid.strip("',/\n")))
			databaseConfig.commit()
			embed = discord.Embed(title="Remove HWID Ban ({})".format(hwid.strip("',/\n")), color=discord.Colour.green())
			embed.add_field(name="Status", value="Success", inline=False)
			await ctx.reply(embed=embed, mention_author=True)
			print("[Query] " + "[DELETE FROM banned WHERE hwid = %s] was queried to database by %s.", (hwid.strip("',/\n"), ctx.author.name))
		except Exception as exc:
			print("[Exception] " + exc.replace("\n", " "))
			embed = discord.Embed(title="Remove HWID Ban ({})".format(hwid.strip("',/\n")), color=discord.Colour.red())
			embed.add_field(name="Error", value="Internal Server Error\n\n{}".format(exc), inline=False)
			await ctx.reply(embed=embed, mention_author=True)

	@commands.group(pass_context=True, case_insensitive=True)
	@authorized()
	async def lookup(self, ctx: commands.Context):
		pass

	@lookup.command(pass_context=True, ignore_extra=True)
	@authorized()
	async def bomb(self, ctx: commands.Context, *, id: str):
		cursor.execute("SELECT * FROM bombs WHERE id=%s", (id.strip("',/\n")))
		row = cursor.fetchone()
		try:
			embed = discord.Embed(title="Bomb Lookup ({})".format(id.strip("',/\n")), color=discord.Colour.green())
			embed.add_field(name="Target", value=row.get("target"), inline=False)
			embed.add_field(name="Time", value=row.get("time"), inline=False)
			await ctx.reply(embed=embed, mention_author=True)
			print("[Query] " + "[SELECT * FROM bombs WHERE id=%s] was queried to database by %s.", (id.strip("',/\n"), ctx.author.name))
		except Exception as exc:
			print("[Exception] " + exc.replace("\n", " "))
			embed = discord.Embed(title="Session Lookup ({})".format(id.strip("',/\n")), color=discord.Colour.red())
			embed.add_field(name="Error", value="Invalid Session ID (User Error / Server Error)", inline=False)
			await ctx.reply(embed=embed, mention_author=True)

	@lookup.command(pass_context=True, ignore_extra=True)
	@authorized()
	async def session(self, ctx: commands.Context, *, id: str):
		cursor.execute("SELECT * FROM sessions WHERE id=%s", (id.strip("',/\n")))
		row = cursor.fetchone()
		try:
			embed = discord.Embed(title="Session Lookup ({})".format(id.strip("',/\n")), color=discord.Colour.green())
			embed.add_field(name="HWID", value=row.get("hwid"), inline=False)
			embed.add_field(name="Computer Name", value=row.get("computer_name"), inline=False)
			embed.add_field(name="Local Username", value=row.get("local_user"), inline=False)
			embed.add_field(name="Connected SSID", value=row.get("ssid"), inline=False)
			embed.add_field(name="Public IPv4", value=row.get("ipv4"), inline=False)
			embed.add_field(name="Discord", value=row.get("cord"), inline=False)
			embed.add_field(name="Number of Bombs Dropped", value=row.get("dropped_int"), inline=False)
			embed.add_field(name="ID(s)", value=row.get("dropped_ids"), inline=False)
			await ctx.send(embed=embed, mention_author=True)
			print("[Query] " + "[SELECT * FROM sessions WHERE id='{}'] was queried to database by {}.".format(id.strip("',/\n"), ctx.author.name))
		except Exception as exc:
			print("[Exception] " + exc.replace("\n", " "))
			embed = discord.Embed(title="Session Lookup ({})".format(id.strip("',/\n")), color=discord.Colour.red())
			embed.add_field(name="Error", value="Invalid Session ID (User Error / Server Error)", inline=False)
			await ctx.send(embed=embed, mention_author=True)


def setup(bot: commands.Bot):
	bot.add_cog(Sms(bot))

while __name__ == "__main__":
	try:
		databaseConfig.ping(reconnect=False)
	except Exception as exc:
		logging.log(logging.CRITICAL, exc)
		logging.log(logging.INFO, "Attempting to reconnect to MySQL database in '{}'".format(__file__[:-3]))
		databaseConfig = pymysql.connect(
			host=tragedy.dotenvVar("mysqlServer"),
			user="root",
			password=tragedy.dotenvVar("mysqlPassword"),
			port=3306,
			database="sms",
			charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor,
			read_timeout=5,
			write_timeout=5,
			connect_timeout=5,
			autocommit=True
			)