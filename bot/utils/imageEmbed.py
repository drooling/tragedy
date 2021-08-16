import json
import enum

import discord
from discord.colour import Color


class FileType(enum.Enum):
	PNG = '.png'
	MP4 = '.mp4'

class ImageEmbed(discord.Embed):

    @classmethod
    def make(cls, command, extension: FileType = FileType.PNG):
        try:
            title = json.load(
                open("bot/assets/json/imageEmbedTitles.json", "r"))[command]
        except KeyError:
            title = str(command).title().strip()

        embedImage = discord.Embed(title=title, color=Color.green())
        embedImage.set_image(
            url="attachment://linktr.ee_incriminating{}".format(
                extension.value
            )
        )
        return embedImage
