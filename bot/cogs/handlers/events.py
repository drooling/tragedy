# -*- coding: utf-8 -*-

import asyncio
import sys
import traceback
from bot.utils import *
from discord.colour import Color
from discord.ext import commands
import discord
import logging
import datetime
import bot.utils.utilities as tragedy
import pymysql.cursors
import bot.utils.utilities as tragedy

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

class Events(commands.Cog, command_attrs=dict(hidden=True)):
	def __init__(self, bot):
		self.bot = bot
		self.loop = asyncio.get_event_loop()

	@commands.Cog.listener()
	async def on_message(self, payload: discord.Message):
		if payload.author == self.bot.user:
			return
		elif self.bot.user in payload.mentions and payload.mention_everyone is False:
			cursor.execute("SELECT * FROM prefix WHERE guild=%s", (payload.guild.id))
			prefix = cursor.fetchone().get('prefix')
			cursor.execute("SELECT * FROM var")
			inviteURL = [row['inviteURL'] for row in cursor.fetchall()][0]
			embed = discord.Embed(title="Hi !", description="My name is {} ! My prefix for this server is \"{}\"\nTo invite me to your server click [Here!]({}).".format(self.bot.user.name, prefix, inviteURL), color = Color.green())
			await payload.reply(embed=embed, mention_author=True)
		else:
			return

#	@commands.Cog.listener()
#	async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
#		try:
#			channel = sorted([chan for chan in member.guild.channels if chan.permissions_for(member.guild.me).send_messages and isinstance(chan, discord.TextChannel)], key=lambda x: x.position)[0]
#			async def play_source(self, voice_client): # play_source function is pasted from stackoverflow not gonna lie
#				source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("./assets/marski/{}".format(random.choice(os.listdir("./assets/marski"))), executable="./assets/ffmpeg.exe"))
#				voice_client.play(source, after=lambda e: self.bot.loop.create_task(play_source(self, voice_client)))
#				voice_client.source.volume = 100
#			if before.channel is not None and after.channel is None:
#				voiceClient = discord.utils.get(self.bot.voice_clients, guild = member.guild)
#				if voiceClient.channel != None:
#					if len(voiceClient.channel.members) == 1:
#						await channel.send("{} FOLDEDDDDDD LEFT VC PUSSY".format(member.mention))
#						await asyncio.sleep(3)
#						await voiceClient.disconnect()
#						return
#			#with open("./assets/pack.json", "r") as list:
#				#if member.id in json.load(list)["pack"] and after.channel is not None:
#			if before.channel is None and after.channel is not None:
#				instance = await after.channel.connect()
#				self.bot.loop.create_task(play_source(self, instance))
#				return
#			if before.self_deaf == False and after.self_deaf == True:
#				await channel.send("{} UNDEAFEN YOU BITCH MADE LITTLE BOY, BIG HEAD, RETARDED SHEEP LOOKIN ASS NIGGA IM REALLY BOUTTA GET TO THE PACKIN ON YOU".format(member.mention))
#				return
#			if before.self_deaf == True and after.self_deaf == False:
#				await channel.send("{} THATS WHAT I THOUGHT RETARD UNDEAFEN FOR DADDY YOU LITTLE PUSSY".format(member.mention))
#				return
#			if before.self_mute == False and after.self_mute == True:
#				await channel.send("{} MUTED LMFAOOO BITCHEDDDD".format(member.mention))
#				return
#		except Exception as exc:
#			print("[Exception] {}".format(exc))
#			pass


	@commands.Cog.listener()
	async def on_guild_join(self, guild: discord.Guild):
		try:
			cursor.execute("INSERT INTO prefix (guild) VALUES (%s)", (guild.id))
			databaseConfig.commit()
			print("[Logging] Added {} to prefix database.".format(guild.id))
		except Exception as exc:
			tragedy.logError(exc)
		try:
			embed = discord.Embed(title="Hello !", description="My name is {}, thank you for inviting me to your server ! To view my commands type \"xv help\" in the chat.".format(self.bot.user.name), color=Color.green())
			await guild.owner.send(embed=embed)
		except:
			pass

	@commands.Cog.listener()
	async def on_guild_remove(self, guild: discord.Guild):
		try:
			cursor.execute("DELETE FROM prefix WHERE guild=%s", (guild.id))
			databaseConfig.commit()
		except Exception as exc:
			exc_type, exc_value, exc_tb = sys.exc_info()
			exception = traceback.format_exception(exc_type, exc_value, exc_tb)
			logging.log(logging.ERROR, exception)
		except:
			pass

	@commands.Cog.listener()
	async def on_command_completion(self, ctx):
		logging.log(20, "{}:'{}' EXECUTED BY {} IN '{}' ({}:{})".format(datetime.datetime.now(), ctx.command.qualified_name, ctx.author, ctx.guild.name, ctx.guild.id, ctx.guild.shard_id))

	@commands.Cog.listener()
	async def on_ready(self):
		await self.bot.wait_until_ready()

def setup(bot):
	bot.add_cog(Events(bot))

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
			database="tragedy",
			charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor,
			read_timeout=5,
			write_timeout=5,
			connect_timeout=5,
			autocommit=True
			)