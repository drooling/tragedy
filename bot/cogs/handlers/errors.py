import contextlib
import difflib

import bot.utils.utilities as tragedy
import discord
from bot.utils.classes import NotGuildOwner, NotVoter, WelcomeNotConfigured
from discord.ext import commands
from discord.ext.commands import *


class Errors(commands.Cog, name="on command error"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.commandList = list()
		self.on_cog_load()

	def on_cog_load(self):
		for cmd in self.bot.commands:
			self.commandList.append(cmd.qualified_name)

	@commands.Cog.listener()
	async def on_command_error(self, ctx: commands.Context, error):
		if isinstance(error, NotOwner):
			return
		else:
			if isinstance(error, commands.CommandOnCooldown):
				embed = discord.Embed(title="Oops !",
									  description="slow down you silly goose.",
									  color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.DisabledCommand):
				embed = discord.Embed(title="Oops !",
									  description="That command is disabled at the moment you silly goose",
									  color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, CommandNotFound):
				description = "Command not found.\n\n**Did you Mean?:**\n{0}".format('`' + ('` `'.join(difflib.get_close_matches(ctx.invoked_with, self.commandList))) + '`')
				embed = discord.Embed(title="Error 404", color=discord.Color.red(), description=description if not description.endswith("``") else "Command not found.")
				if embed.description != "Command not found.":
					await ctx.send(embed=embed)
				else:
					return
			elif isinstance(error, MissingPermissions):
				embed = discord.Embed(title="Oops !",
									  description="You need `{0}` permissions for that".format(
										  ' '.join(error.missing_perms[0].split('_')).title()),
									  color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.BotMissingPermissions):
				embed = discord.Embed(title="Oops !", description="I need `{0}` permissions to do that".format(
					' '.join(error.missing_perms[0].split('_')).title()), color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, NotVoter):
				embed = discord.Embed(title="Oops !", description="That command is only for voters you silly goose !\n To vote for tragedy and get access to that command click [here!](https://top.gg/bot/875514281993601055/vote)", color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, CheckFailure):
				embed = discord.Embed(title="Oops !", description="{} you silly goose".format(
					error.args[0]
				), color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, WelcomeNotConfigured):
				embed = discord.Embed(title="Oops !", description="The `auto-welcome` feature is not fully configured yet !\n Use `welcome setup` to configure it.", color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, NotGuildOwner):
				embed = discord.Embed(title="Oops !", description="That command can only be used by the server owner.", color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.BadArgument):
				embed = discord.Embed(title="Oops !", description="{} you silly goose".format(
				   error.args[0]), color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.MissingRequiredArgument):
				embed = discord.Embed(title="Oops !",
									  description="You're missing the `{0}` argument you silly goose".format(
										  error.param), color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			else:
				with contextlib.suppress(Exception):
					await tragedy.report(self, ctx, error)

def setup(bot):
	bot.add_cog(Errors(bot))
