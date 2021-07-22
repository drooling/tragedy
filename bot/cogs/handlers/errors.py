import discord
from discord.ext import commands
from discord.ext.commands import MissingPermissions, CheckFailure, CommandNotFound, NotOwner
import asyncio
import bot.resources.utilities as tragedy


class Errors(commands.Cog, name="on command error"):
	def __init__(self, bot:commands.Bot):
		self.bot = bot
		
	@commands.Cog.listener()
	async def on_command_error(self, ctx: commands.Context, error:commands.CommandError):
		if ctx.command.has_error_handler() == True:
			return
		else:
			if isinstance(error, NotOwner):
				embed = discord.Embed(title="Error", description="You do not own me bitch, that shit is owner ONLY", color=discord.Color.red())
				temp = await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.CommandOnCooldown):
				embed = discord.Embed(title="Error", description="WAIT A FUCKIN MINUTE STOP SPAMMIN ME IM SLOW", color=discord.Color.red())
				temp = await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.DisabledCommand):
				embed = discord.Embed(title="Error", description="That command is disabled at the moment you silly goose", color=discord.Color.red())
				temp = await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, CommandNotFound):
				embed = discord.Embed(title="Error", description="That command does not exist you silly goose", color=discord.Color.red())
				temp = await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, MissingPermissions):
				embed = discord.Embed(title="Error", description="That command required permissions ({}) you do not possess you silly goose".format(' and '.join(error.missing_perms).removeprefix("and ")), color=discord.Color.red())
				temp = await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.BotMissingPermissions):
				embed = discord.Embed(title="Error", description="I need the \"{}\" permission to do that".format(' and '.join(error.missing_perms).removeprefix("and ")), color=discord.Color.red())
				temp = await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, CheckFailure):
				embed = discord.Embed(title="Error", description="That command requires roles/permissions you do not possess you silly goose", color=discord.Color.red())
				temp = await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.BadArgument):
				embed = discord.Embed(title="Error", description="You supplied an invalid arguments ({}) you silly goose".format(' and '.join(error.param).removeprefix("and ")), color=discord.Color.red())
				temp = await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.MissingRequiredArgument):
				embed = discord.Embed(title="Error", description="You're missing the \"{}\" argument you silly goose".format(error.param), color=discord.Color.red())
				temp = await ctx.reply(embed=embed, mention_author=True)
			elif isinstance(error, commands.UnexpectedQuoteError):
				embed = discord.Embed(title="Error", description="That quote isn't supposed to be there you silly goose", color=discord.Color.red())
				temp = await ctx.reply(embed=embed, mention_author=True)
			else:
				embed = discord.Embed(title="Error", description="Something went wrong and we're not quite sure what", color=discord.Color.red())
				temp = await ctx.reply(embed=embed, mention_author=True)
				tragedy.logError(error)
			try:
				await asyncio.sleep(15)
				await temp.delete()
				await ctx.message.delete()
			except Exception as exc:
				tragedy.logError(exc)

def setup(bot):
	bot.add_cog(Errors(bot))
