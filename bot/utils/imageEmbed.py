import json

import discord
from discord.colour import Color
from discord.embeds import Embed

class ImageEmbed(Embed):

	@classmethod
	def make(cls, command, extension='.png'):
		try:
			title = json.load(open("bot/assets/json/imageEmbedTitles.json", "r"))[command]
		except KeyError:
			title = str(command).title().strip()

		embedImage = discord.Embed(title=title, color=Color.green())
		embedImage.set_image(
			url="attachment://linktr.ee_incriminating{}".format(
				extension
				)
			)
		return embedImage
