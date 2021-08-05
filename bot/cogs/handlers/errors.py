import discord
from discord.ext import commands
from discord.ext.commands import *

import bot.utils.utilities as tragedy


class Errors(commands.Cog, name="on command error"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

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
				pass
			elif isinstance(error, MissingPermissions):
				embed = discord.Embed(title="Oops !",
									  description="That command required permissions ({}) you do not possess you silly goose".format(
										  ' and '.join(error.missing_perms).removeprefix(" and ")),
									  color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.BotMissingPermissions):
				embed = discord.Embed(title="Oops !", description="I need the \"{}\" permission(s) to do that".format(
					' and '.join(error.missing_perms).removeprefix(" and ")), color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, CheckFailure):
				embed = discord.Embed(title="Oops !", description="{} you silly goose".format(
					" and ".join(error.args).removeprefix(" and ")), color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.BadArgument):
				embed = discord.Embed(title="Oops !", description="{} you silly goose".format(
					" and ".join(error.args).removeprefix(" and ")), color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.MissingRequiredArgument):
				embed = discord.Embed(title="Oops !",
									  description="You're missing the \"{}\" argument you silly goose".format(
										  error.param), color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.UnexpectedQuoteError):
				embed = discord.Embed(title="Oops !",
									  description="That quote isn't supposed to be there you silly goose",
									  color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, CommandInvokeError):
				if str(error).endswith("Missing Permissions"):
					embed = discord.Embed(title="Oops !",
									  description="I am not high enough in the role heirachy to do that you silly goose.",
									  color=discord.Color.red())
					await ctx.reply(embed=embed, mention_author=True)
				else:
					await tragedy.report(self, ctx, error)
			else:
				await tragedy.report(self, ctx, error)


def setup(bot):
	bot.add_cog(Errors(bot))
