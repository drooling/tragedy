import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from PIL import Image, ImageOps
import io
import aiohttp

class ImageManipulation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, BucketType.member)
    async def invert(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = await member.avatar_url_as(format='png', size=1024).read()
        with io.BytesIO(avatar) as buffer:
            image = Image.open(buffer).convert("RGB")
            inverted = ImageOps.invert(image)
            final = io.BytesIO()
            inverted.save(final, format='PNG')
            final.seek(0)
            await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

    @commands.command()
    @commands.cooldown(1, 5, BucketType.member)
    async def gay(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = await member.avatar_url_as(format='png', size=1024).read()
        with io.BytesIO(avatar) as buffer:
            image = Image.open(buffer)
            

def setup(bot: commands.Bot):
    bot.add_cog(ImageManipulation(bot))