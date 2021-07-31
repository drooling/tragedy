import io

import aiohttp
import discord
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from bot.utils.utilities import *


class Images(commands.Cog, description="Commands that manipulate images"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.aiohttp = aiohttp.ClientSession()
		self.assets = "bot/assets/"

	@commands.command(description="Inverts user's avatar", help="invert [member]")
	@commands.cooldown(1, 5, BucketType.member)
	async def invert(self, ctx, member: commands.MemberConverter = None):
		member = ctx.author if not member else member
		avatar = await member.avatar_url_as(format='png', size=1024).read()
		with io.BytesIO(avatar) as buffer:
			image = Image.open(buffer).convert("RGB")
			inverted = ImageOps.invert(image)
			final = io.BytesIO()
			inverted.save(final, format='PNG')
			final.seek(0)
			await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

	@commands.command(description="Blurs user's avatar", help="blur [member]")
	@commands.cooldown(1, 5, BucketType.member)
	async def blur(self, ctx, member: commands.MemberConverter = None):
		member = ctx.author if not member else member
		avatar = await member.avatar_url_as(format='png', size=1024).read()
		with io.BytesIO(avatar) as buffer:
			image = Image.open(buffer).convert("RGB")
			blurred = image.filter(ImageFilter.GaussianBlur)
			final = io.BytesIO()
			blurred.save(final, format='PNG')
			final.seek(0)
			await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

	@commands.command(description="Posterize's user's avatar", help="posterize [member]")
	@commands.cooldown(1, 5, BucketType.member)
	async def posterize(self, ctx, member: commands.MemberConverter = None):
		member = ctx.author if not member else member
		avatar = await member.avatar_url_as(format='png', size=1024).read()
		with io.BytesIO(avatar) as buffer:
			image = Image.open(buffer).convert("RGB")
			posterized = ImageOps.posterize(image, 2)
			final = io.BytesIO()
			posterized.save(final, format='PNG')
			final.seek(0)
			await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

	@commands.command(description="Convert user's avatar to black and white", help="grayscale [member]",
	                  aliases=["baw", "b&w"])
	@commands.cooldown(1, 5, BucketType.member)
	async def grayscale(self, ctx, member: commands.MemberConverter = None):
		member = ctx.author if not member else member
		avatar = await member.avatar_url_as(format='png', size=1024).read()
		with io.BytesIO(avatar) as buffer:
			image = Image.open(buffer).convert("RGB")
			grayscale = ImageOps.grayscale(image)
			final = io.BytesIO()
			grayscale.save(final, format='PNG')
			final.seek(0)
			await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

	@commands.command(aliases=["deepfry", "deepfried"], description="Deep fries user's avatar", help="fry [user]")
	@commands.cooldown(1, 5, type=BucketType.member)
	async def fry(self, ctx, user: commands.MemberConverter = None):
		if user is None:
			async with self.aiohttp.get("https://nekobot.xyz/api/imagegen?type=deepfry&image={}".format(
					str(ctx.author.avatar_url_as(format="png")))) as r:
				res = await r.json()
				embed = discord.Embed(title="Deep Fried {} !".format(ctx.author.name),
				                      color=discord.Color.green()).set_image(url=res['message'])
				await ctx.reply(embed=embed, mention_author=True)
		else:
			async with self.aiohttp.get("https://nekobot.xyz/api/imagegen?type=deepfry&image={}".format(
					str(user.avatar_url_as(format="png")))) as r:
				res = await r.json()
				embed = discord.Embed(title="Deep Fried {} !".format(user.display_name),
				                      color=discord.Color.green()).set_image(url=res['message'])
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
				file.seek(0)
				sendFile = discord.File(file, filename="linktr.ee_incriminating.mp4")
				await ctx.reply(file=sendFile)

	@commands.command(name="triggered", description="Makes person triggered", help="triggered [member]")
	async def _triggered(self, ctx: commands.Context, member: commands.MemberConverter = None):
		async with ctx.typing():
			member = ctx.author if not member else member
			avatar = await member.avatar_url_as(format='png', size=1024).read()
			with io.BytesIO(avatar) as buff:
				avatar = Image.open(buff)
				triggered = Image.open(self.assets + "pillow/triggered.jpg")
				triggered.thumbnail(avatar.size, Image.ANTIALIAS)
				position = 0, avatar.getbbox()[3] - triggered.getbbox()[3]
				avatar.paste(triggered, position)
				final = io.BytesIO()
				avatar.save(final, format="PNG")
				final.seek(0)
				await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

	@commands.command(name="gay", description="Makes person gay", help="gay [member]")
	async def _gay(self, ctx: commands.Context, member: commands.MemberConverter = None):
		async with ctx.typing():
			member = ctx.author if not member else member
			avatar = await member.avatar_url_as(format='png', size=1024).read()
			with io.BytesIO(avatar) as buff:
				avatar = Image.open(buff).resize((480, 480))
				gay = Image.open(self.assets + "pillow/gay.png").convert("RGBA")
				gay.putalpha(128)
				avatar.paste(gay, (0, 0), gay)
				final = io.BytesIO()
				avatar.save(final, format="PNG")
				final.seek(0)
				await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

	@commands.command(name="jail", description="Puts person behind bars", help="jail [member]")
	async def _jail(self, ctx: commands.Context, member: commands.MemberConverter = None):
		async with ctx.typing():
			member = ctx.author if not member else member
			avatar = await member.avatar_url_as(format='png', size=1024).read()
			with io.BytesIO(avatar) as buff:
				avatar = Image.open(buff).resize((400, 400))
				bars = Image.open(self.assets + "pillow/bars.png").convert("RGBA")
				avatar.paste(bars, (0, 0), bars)
				final = io.BytesIO()
				avatar.save(final, format="PNG")
				final.seek(0)
				await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

	@commands.command(name="communist", description="Makes person a communist", help="communist [member]")
	async def _communist(self, ctx: commands.Context, member: commands.MemberConverter = None):
		async with ctx.typing():
			member = ctx.author if not member else member
			avatar = await member.avatar_url_as(format='png', size=1024).read()
			with io.BytesIO(avatar) as buff:
				avatar = Image.open(buff).resize((1000, 1000))
				flag = Image.open(self.assets + "pillow/communist.jpg").convert("RGBA")
				flag.putalpha(128)
				avatar.paste(flag, (0, 0), flag)
				final = io.BytesIO()
				avatar.save(final, format="PNG")
				final.seek(0)
				await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

	@commands.command(name="pan", description="Pan.", help="pan [member]")
	async def _pan(self, ctx: commands.Context, member: commands.MemberConverter = None):
		if member != None and await self.bot.is_owner(member) == True:
			await ctx.send("no.")
			return
		else:
			async with ctx.typing():
				member = ctx.author if not member else member
				avatar = await member.avatar_url_as(format='png', size=1024).read()
				with io.BytesIO(avatar) as buff:
					avatar = Image.open(buff).resize((245, 240))
					pan = Image.open(self.assets + "pillow/pan.jpg")
					pan.paste(avatar, (270, 130))
					final = io.BytesIO()
					panWriter = ImageDraw.Draw(pan)
					font = ImageFont.truetype(self.assets + "fonts/Arial.ttf", 35)
					panWriter.text((410, 15), wrap(font=font, text="@{} dis you??".format(member.name), line_width=325),
					               font=font, fill="Black")
					pan.save(final, format="PNG")
					final.seek(0)
					await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

	@commands.command(name="presentation", description="Makes lisa simpson presentation meme with your text",
	                  help="presentation <message> [member]")
	async def _presentation(self, ctx: commands.Context, *, message: str, member: commands.MemberConverter = None):
		async with ctx.typing():
			member = ctx.author if not member else member
			avatar = await member.avatar_url_as(format='png', size=1024).read()
			with io.BytesIO(avatar) as buff:
				avatar = Image.open(buff).resize((85, 75))
				presentation = Image.open(self.assets + "pillow/presentation.bmp")
				presentation.paste(avatar, (175, 280))
				final = io.BytesIO()
				presentationWriter = ImageDraw.Draw(presentation)
				font = ImageFont.truetype(self.assets + "fonts/Arial.ttf", 50)
				presentationWriter.text((120, 70), wrap(font=font, text=message, line_width=450), font=font,
				                        fill="Black")
				presentation.save(final, format="PNG")
				final.seek(0)
				await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

	@commands.command(name="warned", description="Warned by the judge", help="warned [member]")
	async def _warned(self, ctx: commands.Context, member: commands.MemberConverter = None):
		async with ctx.typing():
			member = ctx.author if not member else member
			avatar = await member.avatar_url_as(format='png', size=1024).read()
			with io.BytesIO(avatar) as buff:
				avatar = Image.open(buff).resize((75, 70))
				warned = Image.open(self.assets + "pillow/warn.jpg")
				warned.paste(avatar, (300, 545))
				final = io.BytesIO()
				warned.save(final, format="PNG")
				final.seek(0)
				await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

	@commands.command(name="menace", description="Shows how much of a menace to society the specified person is",
	                  help="menace <member>")
	async def _menace(self, ctx: commands.Context, member: commands.MemberConverter):
		async with ctx.typing():
			if await self.bot.is_owner(member):
				await ctx.send("no.")
				return
			GrievanceAvatar = await member.avatar_url_as(format='png', size=1024).read()
			avatar = await ctx.author.avatar_url_as(format='png', size=1024).read()
			with io.BytesIO(GrievanceAvatar) as buff:
				Grief = Image.open(buff).resize((90, 90))
				avatar = Image.open(io.BytesIO(avatar)).resize((135, 120))
				base = Image.open(self.assets + "pillow/ruin.jpg")
				base.paste(avatar, (110, 15))
				base.paste(Grief, (320, 40))
				baseWriter = ImageDraw.Draw(base)
				font = ImageFont.truetype(self.assets + "fonts/Arial.ttf", 35)
				baseWriter.text((30, 150), wrap(font=font, text="@{} chillin".format(ctx.author.name), line_width=240),
				                font=font, fill="Black")
				final = io.BytesIO()
				base.save(final, format="PNG")
				final.seek(0)
				await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

	@commands.command(name="burn", description="Burns the specified text", help="burn <message>")
	async def _burn(self, ctx: commands.Context, *, message: str):
		burnit = Image.open(self.assets + "pillow/burnit.bmp")
		burnitWriter = ImageDraw.Draw(burnit)
		font = ImageFont.truetype(self.assets + "fonts/Arial.ttf", 50)
		burnitWriter.text((105, 185), wrap(font, text=message, line_width=365), font=font, fill="Black")
		final = io.BytesIO()
		burnit.save(final, format="PNG")
		final.seek(0)
		await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

	@commands.command(name="match", description="Tinder match", help="match <lover1> [lover2]")
	async def _match(self, ctx: commands.Context, lover1: commands.MemberConverter, lover2: commands.MemberConverter = None):
		async with ctx.typing():
			lover2 = ctx.author if not lover2 else lover2
			lover1 = await lover1.avatar_url_as(format='png', size=1024).read()
			lover2 = await lover2.avatar_url_as(format='png', size=1024).read()
			with io.BytesIO(lover1) as buff:
				lover1 = Image.open(buff).resize((140, 145))
				lover2 = Image.open(io.BytesIO(lover2)).resize((145, 145))
				base = Image.open(self.assets + "pillow/match.bmp")
				base.paste(lover1, (20, 157))
				base.paste(lover2, (170, 155))
				final = io.BytesIO()
				base.save(final, format="PNG")
				final.seek(0)
				await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))

	@commands.is_nsfw()
	@commands.command(name="fuck", description="Rail tf outta specified user", help="fuck <user>")
	async def _fuck(self, ctx: commands.Context, user: commands.MemberConverter):
		async with ctx.typing():
			slut = user
			slutAvBytes = await slut.avatar_url_as(format="png", size=1024).read()
			with io.BytesIO(slutAvBytes) as slutAvIO:
				rail = Image.open(self.assets + "pillow/rail.gif")
				slutAv = Image.open(slutAvIO).resize((80, 85))
				gif = list()
				for i in range(0, rail.n_frames):
					rail.seek(i)
					frame = rail.copy().convert('RGBA')
					frame.paste(slutAv, (155, 110), slutAv)
					gif.append(frame)
				final = io.BytesIO()
				gif[0].save(final, format='gif', save_all=True, append_images=gif[1:], loop=0, optimize=True)
				final.seek(0)
				await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.gif"))
				
	#@commands.command(name="profile", description="Generates user profile", help="profile [user]")
	#async def _profile(self, ctx: commands.Context, user: commands.MemberConverter):
	#	try:
	#		async with ctx.typing():
	#			avatarBytes = await user.avatar_url_as(format="png", size=1024).read()
	#			with Image.open(io.BytesIO(avatarBytes)).resize((135, 130)).convert("RGBA") as avatar:
	#				base = Image.open(self.assets + "pillow/profile.png").convert("RGBA")
	#				end = Image.new("RGBA", base.size)
	#				font = ImageFont.truetype(self.assets + "fonts/Arial.ttf", 10)
	#				baseWriter = ImageDraw.Draw(base)
	#				baseWriter.text((15, 175), wrap(font, text=str(user.name + "#" + user.discriminator), line_width=135), font=font, fill="White")
	#				end.paste(avatar, (15, 35), avatar)
	#				end.paste(base, (0, 0), base)
	#				end = end.convert("RGBA")
	#				final = io.BytesIO()
	#				end.save(final, format="PNG")
	#				final.seek(0)
	#				await ctx.send(file=discord.File(final, filename="linktr.ee_incriminating.png"))
	#	except Exception as exc:
	#		pprint.pprint(exc)

def setup(bot: commands.Bot):
	bot.add_cog(Images(bot))
