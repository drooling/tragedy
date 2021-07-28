import discord
from discord.ext import commands
from discord.ext.commands import MissingPermissions, CheckFailure, CommandNotFound, NotOwner

import bot.utils.utilities as tragedy


class Errors(commands.Cog, name="on command error"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
		if isinstance(error, NotOwner):
			return
		else:
			if isinstance(error, NotOwner):
				embed = discord.Embed(title="Error", description="You do not own me bitch, that shit is owner ONLY",
									  color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.CommandOnCooldown):
				embed = discord.Embed(title="Error",
									  description="slow down you silly goose or imma have to break ya nigga nigga kneecaps (my great uncle's grandma's cousin's dog's right nut was black btw so i can say it)",
									  color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.DisabledCommand):
				embed = discord.Embed(title="Error",
									  description="That command is disabled at the moment you silly goose",
									  color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, CommandNotFound):
				pass
			elif isinstance(error, MissingPermissions):
				embed = discord.Embed(title="Error",
									  description="That command required permissions ({}) you do not possess you silly goose".format(
										  ' and '.join(error.missing_perms).removeprefix(" and ")),
									  color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.BotMissingPermissions):
				embed = discord.Embed(title="Error", description="I need the \"{}\" permission(s) to do that".format(
					' and '.join(error.missing_perms).removeprefix(" and ")), color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, CheckFailure):
				embed = discord.Embed(title="Error", description="{} you silly goose".format(
					" and ".join(error.args).removeprefix(" and ")), color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.BadArgument):
				embed = discord.Embed(title="Error", description="{} you silly goose".format(
					" and ".join(error.args).removeprefix(" and ")), color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.MissingRequiredArgument):
				embed = discord.Embed(title="Error",
									  description="You're missing the \"{}\" argument you silly goose".format(
										  error.param), color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.UnexpectedQuoteError):
				embed = discord.Embed(title="Error",
									  description="That quote isn't supposed to be there you silly goose",
									  color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
			else:
				embed = discord.Embed(title="Error", description="Something went wrong and we're not quite sure what",
									  color=discord.Color.red())
				await ctx.reply(embed=embed, mention_author=True)
				tragedy.logError(error)


def setup(bot):
	bot.add_cog(Errors(bot))
