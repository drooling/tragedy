import json

import discord
from discord.colour import Color
from discord.embeds import Embed

class ImageEmbed(Embed):

	@classmethod
	def from_command(cls, extension='.png', **kwargs):
		command = kwargs.pop("command")
		title = json.load(open("bot/assets/json/imageEmbedTitles.json", "r"))[command] or str(command).title().strip()
		embedImage = discord.Embed(title=title, color=Color.green())
		embedImage.set_image(
			url="attachment://linktr.ee_incriminating{}".format(
				extension
				)
			)
		return embedImage
