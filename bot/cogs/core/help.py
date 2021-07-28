# -*- coding: utf-8 -*-

import contextlib

import discord
from discord.colour import Color
from discord.ext import commands


class HelpEmbed(discord.Embed):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		text = "Use help [command] or help [category] for more information | <required> - [optional]"
		self.set_footer(text=text)
		self.color = Color.green()


class Help(commands.HelpCommand):
	def __init__(self):
		super().__init__(
			command_attrs={
				"help": "The help command for the bot",
				"cooldown": commands.Cooldown(1, 3.0, commands.BucketType.user),
				"aliases": ['commands']
			}
		)

	async def send(self, **kwargs):
		await self.get_destination().send(**kwargs)

	async def send_bot_help(self, mapping):
		ctx = self.context
		embed = HelpEmbed()
		usable = 0

		for cog, commands in mapping.items():
			if filtered_commands := await self.filter_commands(commands):
				amount_commands = len(filtered_commands)
				usable += amount_commands
				if cog:
					name = cog.qualified_name
					description = cog.description or "No description"
					embed.add_field(name=f"{name} [{amount_commands}]", value=description, inline=False)
				else:
					pass

		embed.description = f"{usable} commands"
		await self.send(embed=embed)

	async def send_command_help(self, command):
		signature = self.get_command_signature(command)
		embed = HelpEmbed(title=signature,
						  description="```{}```".format(command.description or "No Description Specified By Developer"))

		if cog := command.cog:
			embed.add_field(name="Category", value=cog.qualified_name)

		can_run = "No"
		with contextlib.suppress(commands.CommandError):
			if await command.can_run(self.context):
				can_run = "Yes"

		embed.add_field(name="Enabled?", value=can_run)

		if command._buckets and (cooldown := command._buckets._cooldown):
			embed.add_field(name="Cooldown", value=f"{cooldown.rate} per {cooldown.per:.0f} seconds")

		await self.send(embed=embed)

	async def send_help_embed(self, title, description, commands):
		embed = HelpEmbed(title=title, description=description or "No Description Specified By Developer")

		if filtered_commands := await self.filter_commands(commands):
			for command in filtered_commands:
				embed.add_field(name=command.name, value=command.description or "No Description Specified By Developer")

		await self.send(embed=embed)

	async def send_group_help(self, group):
		title = self.get_command_signature(group)
		await self.send_help_embed(title, group.help, group.commands)

	async def send_cog_help(self, cog):
		title = cog.qualified_name or "No"
		await self.send_help_embed(title, cog.description, cog.get_commands())


def setup(bot):
	bot.help_command = Help()
