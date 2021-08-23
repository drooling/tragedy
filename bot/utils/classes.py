import discord

from enum import Enum
from discord.ext import commands


class NotVoter(commands.CheckFailure):
	pass

class WelcomeNotConfigured(commands.CheckFailure):
    pass
