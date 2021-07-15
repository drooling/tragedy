# -*- coding: utf-8 -*-

import asyncio
import aiohttp
from discord.colour import Color
from discord.ext import commands
import discord
import os
import resources.utilities as tragedy

class Owner(commands.Cog, command_attrs=dict()):
	def __init__(self, bot):
		self.bot = bot
		self.aiohttp = aiohttp.ClientSession()

	@commands.command()
	@commands.is_owner()
	async def reload(self, ctx: commands.Context, *, cogName: str):
		try:
			self.bot.reload_extension("Cogs.{}".format(cogName))
			print("[Injection] Successfully Administered Another Dose Of Cogs.{}".format(cogName))
			embed = discord.Embed(title="Cog reloaded", description="Successfully Reloaded \"Cogs.{}\"".format(cogName), color=discord.Color.green())
			temp = await ctx.reply(embed=embed, mention_author=True)
			await asyncio.sleep(5)
			await temp.delete()
			await ctx.message.delete()
		except Exception as exc:
			tragedy.logError(exc)
			embed = discord.Embed(title="Error", description="That Cog does not exist / failed to reload Cog", color=discord.Color.red())
			temp = await ctx.reply(embed=embed, mention_author=True)
			await asyncio.sleep(5)
			await temp.delete()
			await ctx.message.delete()

	@commands.command()
	@commands.is_owner()
	async def restart(self, ctx):
		os.system('clear')
		reloaded = []
		errorReloading = []
		for filename in os.listdir("Cogs"):
			if filename.endswith(".py"):
				try:
					self.bot.reload_extension("Cogs.{}".format(filename[:-3]))
					reloaded.append("Cogs.{}".format(filename[:-3]))
					print("[Injection] Successfully Injected Cogs.{}".format(filename[:-3]))
				except Exception as exc:
					errorReloading.append("Cogs.{}".format(filename[:-3]))
					tragedy.logError(exc)
		print("[Injection] Finished Injecting Cogs into {}.".format(self.bot.user))
		reloaded = '\n'.join(reloaded)
		errorReloading = '\n'.join(errorReloading)
		embed = discord.Embed(title="All Cogs Reloaded", description="**Successfully Reloaded**\n{}\n**Error Reloading**\n{}".format(reloaded, "None" if errorReloading == None else errorReloading), color=discord.Color.green())
		temp = await ctx.reply(embed=embed, mention_author=True)
		await asyncio.sleep(5)
		await temp.delete()
		await ctx.message.delete()

	@commands.command(aliases=["switch"])
	@commands.is_owner()
	async def toggle(self, ctx, *, command):
		command = self.bot.get_command(command)

		if command is None:
			temp = await ctx.reply(embed=discord.Embed(title="Error", description="That command does not exist.", color=discord.Color.red()), mention_author=True)
			await asyncio.sleep(15)
			await temp.delete()
			await ctx.message.delete()
	
		elif ctx.command == command:
			temp = await ctx.reply(embed=discord.Embed(title="Error", description="You can't disable the disable command you fuckhead.", color=discord.Color.red()), mention_author=True)
			await asyncio.sleep(15)
			await temp.delete()
			await ctx.message.delete()

		else:
			command.enabled = not command.enabled
			ternary = "enabled" if command.enabled else "disabled"
			temp = await ctx.reply(embed=discord.Embed(title=str(command).title(), description="{} was successfully {}".format(str(command).title(), ternary), color=discord.Color.green()), mention_author=True)
			await asyncio.sleep(15)
			await temp.delete()
			await ctx.message.delete()

	@commands.command(aliases=['leaked', 'leaks'])
	@commands.is_owner()
	async def breaches(self, ctx, *query):
		for _query in enumerate(query):
			combos = []
			endpoint = "https://leakcheck.net/api/?key={}&check={}&type=auto".format(tragedy.dotenvVar("leakcheckKey"), _query)
			async with self.aiohttp.get(endpoint) as _response:
				jObj = await _response.json()
				if len(jObj['result']) > 0:
					for _index in enumerate(jObj['result']):
						combos.append(_index['line'])
					description = '\n'.join(combos)
				else:
					description = "No Breaches Found."
			embed = discord.Embed(title="Breaches for \"{}\"".format(_query), description=description, color=Color.green())
			await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Owner(bot))