import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from PIL import Image, ImageOps
import io
import aiohttp

class ImageManipulation(commands.Cog, description="Commands that manipulate images"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.command(description="Inverts user's avatar", help="invert [member]")
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

	@commands.command(aliases=["deepfry", "deepfried"], description="Deep fries user's avatar", help="fry [user]")
	@commands.cooldown(1, 5, type=BucketType.member)
	async def fry(self, ctx, user: discord.Member = None):
		if user is None:
			async with self.aiohttp.get("https://nekobot.xyz/api/imagegen?type=deepfry&image={}".format(str(ctx.author.avatar_url_as(format="png")))) as r:
				res = await r.json()
				embed = discord.Embed(title="Deep Fried {} !".format(ctx.author.name), color=discord.Color.green()).set_image(url=res['message'])
				await ctx.reply(embed=embed, mention_author=True)
		else:
			async with self.aiohttp.get("https://nekobot.xyz/api/imagegen?type=deepfry&image={}".format(str(user.avatar_url_as(format="png")))) as r:
				res = await r.json()
				embed = discord.Embed(title="Deep Fried {} !".format(user.display_name), color=discord.Color.green()).set_image(url=res['message'])
				await ctx.reply(embed=embed, mention_author=True)

	@commands.command(description="Returns video of obama saying specified phrase", help="obama [message]")
	@commands.cooldown(1, 5, BucketType.member)
	async def obama(self, ctx, *, message: str = None):
		if message is None:
			message = "tragedy is the best discord bot!"
		form_data = aiohttp.FormData()
		form_data.add_field("input_text", message)
		async with self.aiohttp.post("http://talkobamato.me", data=form_data) as request:
			key = request.url.query["speech_key"]
			direct = "http://www.talkobamato.me/synth/output/{}/obama.mp4".format(key)
			async with self.aiohttp.get(direct) as video:
				file = io.BytesIO(bytes(await video.read()))
				sendFile = discord.File(file, filename="linktr.ee_incriminating.mp4")
				file.flush()
				file.close()
				await ctx.reply(file=sendFile)

	@commands.command(enabled=False) #In progress
	@commands.cooldown(1, 5, BucketType.member)
	async def gay(self, ctx, member: discord.Member = None):
		member = ctx.author if not member else member
		avatar = await member.avatar_url_as(format='png', size=1024).read()
		with io.BytesIO(avatar) as buffer:
			image = Image.open(buffer)


def setup(bot: commands.Bot):
	bot.add_cog(ImageManipulation(bot))