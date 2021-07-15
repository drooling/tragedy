# -*- coding: utf-8 -*-

import asyncio
from discord.ext import commands
import discord
from discord.colour import Color
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import command
from captcha.image import ImageCaptcha
import pymysql.cursors
import resources.utilities as tragedy

databaseConfig = pymysql.connect(
	host=tragedy.dotenvVar("mysqlServer"),
	user="root",
	password=tragedy.dotenvVar("mysqlPassword"),
	port=3306,
	database="tragedy",
	charset='utf8mb4',
	cursorclass=pymysql.cursors.DictCursor,
	read_timeout=5,
	write_timeout=5,
	connect_timeout=5,
	autocommit=True
	)

cursor = databaseConfig.cursor()

SqlQuery = "SELECT * FROM captcha WHERE guild='{}'"

class Captcha(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.chars = tragedy.randomString(5)

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		cursor.execute("SELECT * FROM captcha WHERE guild='{}'".format(member.guild.id))
		row = cursor.fetchone()
		if row.get("enabled") != "true":
			pass
		else:
			generator = ImageCaptcha(width = 280, height = 90)
			generatedData = generator.generate(self.chars) 
			generator.write(self.chars, './resources/temp/CAPTCHA.png')
			cursor.execute(SqlQuery.format(member.guild.id))
			await member.send("Message me \"xv verify captcha\" replacing \"captcha\" with the letters in the image below (all lowercase) to verify in {}".format(member.guild.name))
			await member.send(file=(discord.File("./resources/temp/CAPTCHA.png")))

	@commands.command()
	@commands.dm_only()
	@commands.cooldown(1, 5, BucketType.user)
	async def verify(self, ctx, * code):
		if code != self.chars:
			await ctx.send("Incorrect.")
		else:
			await ctx.send("Correct (havent made it actually do anything yet)")

	@commands.group(pass_context=True, case_insensitive=True)
	@commands.has_guild_permissions(manage_guild=True)
	@commands.guild_only()
	async def captcha(self, ctx):
		pass

	@captcha.command()
	@commands.has_guild_permissions(manage_guild=True)
	@commands.guild_only()
	async def enable(self, ctx):
		global logChannel

		await ctx.reply("What channel would you like the logs to be sent to? (You have 30 seconds to respond)")
		def check(msg):
			return msg.author == ctx.author and msg.channel == ctx.channel and msg.channel_mentions != []
		try:
			reply = await self.bot.wait_for("message", check=check, timeout=30)
			logChannel = reply.channel_mentions[0]
		except asyncio.TimeoutError:
			await ctx.send("You took too long you silly goose!")

		cursor.execute("INSERT INTO captcha (enabled, guild, logChannel) VALUES ('{}', '{}', '{}')".format("true", ctx.guild.id, logChannel.id))
		databaseConfig.commit()
		

	@captcha.command()
	@commands.has_guild_permissions(manage_guild=True)
	@commands.guild_only()
	async def disable(self, ctx):
		pass

def setup(bot):
	bot.add_cog(Captcha(bot))
