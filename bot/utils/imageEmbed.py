import json

import discord
from discord.colour import Color
from discord.embeds import Embed


class ImageEmbed(Embed):
	def __init__(self, extension=".png", **kwargs):
		self.extension = extension
		self.command = kwargs.pop("command")

		def getTitle():
			try:
				return json.load(
					open("bot/assets/json/imageEmbedTitles.json", "r")
				)[self.command]
			except KeyError:
				return str(self.command).title().strip()

		self.title = getTitle()

	def Generate(self):
		embedImage = discord.Embed(title=self.title, color=Color.green())
		embedImage.set_image(
			url="attachment://linktr.ee_incriminating{}".format(self.extension))
		return embedImage
