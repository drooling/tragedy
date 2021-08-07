import io

import aiohttp
import cv2
import discord
import numpy
import urllib.parse
import random
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from bot.utils.imageEmbed import ImageEmbed
from bot.utils.utilities import Utilities


class Images(commands.Cog, description="Commands that manipulate images"):
	def __init__(self, bot):
		self.bot = bot
		self.aiohttp = aiohttp.ClientSession()
		self.assets = "bot/assets/"
		self.fileName = "linktr.ee_incriminating"

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
			await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
						   embed=ImageEmbed(command="invert").Generate())

	@commands.command(description="sketchs user's avatar", help="sketch [member]")
	@commands.cooldown(1, 5, BucketType.member)
	async def sketch(self, ctx, member: commands.MemberConverter = None):
		member = ctx.author if not member else member
		avatar = await member.avatar_url_as(format='png', size=1024).read()
		with io.BytesIO(avatar) as buffer:
			bytesForCV2 = numpy.asarray(bytearray(buffer.read()), dtype=numpy.uint8)
			image = cv2.imdecode(bytesForCV2, cv2.IMREAD_COLOR)
			cv2.waitKey(1)
			sketch, color = cv2.pencilSketch(image, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
			final = io.BytesIO()
			ioImage = Image.fromarray(sketch)
			ioImage.save(final, format='PNG')
			final.seek(0)
			await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
						   embed=ImageEmbed(command="sketch").Generate())

	@commands.command(description="Oil paints user's avatar", help="oil [member]") # https://towardsdatascience.com/painting-and-sketching-with-opencv-in-python-4293026d78b
	@commands.cooldown(1, 5, BucketType.member)
	async def oil(self, ctx, member: commands.MemberConverter = None):
		member = ctx.author if not member else member
		avatar = await member.avatar_url_as(format='png', size=1024).read()
		with io.BytesIO(avatar) as buffer:
			bytesForCV2 = numpy.asarray(bytearray(buffer.read()), dtype=numpy.uint8)
			image = cv2.imdecode(bytesForCV2, cv2.IMREAD_COLOR)
			cv2.waitKey(1)
			oil = cv2.xphoto.oilPainting(image, 7, 1)
			final = io.BytesIO()
			ioImage = Image.fromarray(oil)
			ioImage.save(final, format='PNG')
			final.seek(0)
			await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
						   embed=ImageEmbed(command="oil").Generate())

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
			await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
						   embed=ImageEmbed(command="blur").Generate())

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
			await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
						   embed=ImageEmbed(command="posterize").Generate())

	@commands.command(description="Solarize's user's avatar", help="solarize [member]")
	@commands.cooldown(1, 5, BucketType.member)
	async def solarize(self, ctx, member: commands.MemberConverter = None):
		member = ctx.author if not member else member
		avatar = await member.avatar_url_as(format='png', size=1024).read()
		with io.BytesIO(avatar) as buffer:
			image = Image.open(buffer).convert("RGB")
			solarize = ImageOps.solarize(image, 255)
			final = io.BytesIO()
			solarize.save(final, format='PNG')
			final.seek(0)
			await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
						   embed=ImageEmbed(command="solarize").Generate())

	@commands.command(description="Flip's user's avatar", help="flip [member]")
	@commands.cooldown(1, 5, BucketType.member)
	async def flip(self, ctx, member: commands.MemberConverter = None):
		member = ctx.author if not member else member
		avatar = await member.avatar_url_as(format='png', size=1024).read()
		with io.BytesIO(avatar) as buffer:
			image = Image.open(buffer).convert("RGB")
			flip = ImageOps.flip(image)
			final = io.BytesIO()
			flip.save(final, format='PNG')
			final.seek(0)
			await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
						   embed=ImageEmbed(command="flip").Generate())

	@commands.command(description="Flip's user's avatar", help="mirror [member]")
	@commands.cooldown(1, 5, BucketType.member)
	async def mirror(self, ctx, member: commands.MemberConverter = None):
		member = ctx.author if not member else member
		avatar = await member.avatar_url_as(format='png', size=1024).read()
		with io.BytesIO(avatar) as buffer:
			image = Image.open(buffer).convert("RGB")
			mirror = ImageOps.mirror(image)
			final = io.BytesIO()
			mirror.save(final, format='PNG')
			final.seek(0)
			await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
						   embed=ImageEmbed(command="mirror").Generate())

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
			await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
						   embed=ImageEmbed(command="grayscale").Generate())

	@commands.command(name='achievement')
	@commands.cooldown(1, 10, BucketType.user)
	async def _achievement(self, ctx, *, achievement: str = None):
		achievement = 'linktr.ee/incriminating.' if not achievement else achievement
		encodedAchievement = urllib.parse.quote(achievement)
		url = 'https://minecraftskinstealer.com/achievement/{}/Achievement%20Earned!/{}'.format(random.randrange(40), encodedAchievement)
		await ctx.send(embed=discord.Embed(
			color=discord.Colour.green()
			).set_image(url=url))

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
			direct = "http://www.talkobamato.me/synth/output/{}/obama.mp4".format(
				key)
			async with self.aiohttp.get(direct) as video:
				file = io.BytesIO(bytes(await video.read()))
				file.seek(0)
				sendFile = discord.File(
					file, filename=self.fileName + '.mp4')
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
				await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
							   embed=ImageEmbed(command="triggered").Generate())

	@commands.command(name="gay", description="Makes person gay", help="gay [member]")
	async def _gay(self, ctx: commands.Context, member: commands.MemberConverter = None):
		async with ctx.typing():
			member = ctx.author if not member else member
			avatar = await member.avatar_url_as(format='png', size=1024).read()
			with io.BytesIO(avatar) as buff:
				avatar = Image.open(buff).resize((480, 480))
				gay = Image.open(
					self.assets + "pillow/gay.png").convert("RGBA")
				gay.putalpha(128)
				avatar.paste(gay, (0, 0), gay)
				final = io.BytesIO()
				avatar.save(final, format="PNG")
				final.seek(0)
				await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
							   embed=ImageEmbed(command="gay").Generate())

	@commands.command(name="jail", description="Puts person behind bars", help="jail [member]")
	async def _jail(self, ctx: commands.Context, member: commands.MemberConverter = None):
		async with ctx.typing():
			member = ctx.author if not member else member
			avatar = await member.avatar_url_as(format='png', size=1024).read()
			with io.BytesIO(avatar) as buff:
				avatar = Image.open(buff).resize((400, 400))
				bars = Image.open(
					self.assets + "pillow/bars.png").convert("RGBA")
				avatar.paste(bars, (0, 0), bars)
				final = io.BytesIO()
				avatar.save(final, format="PNG")
				final.seek(0)
				await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
							   embed=ImageEmbed(command="prison").Generate())

	@commands.command(name="communist", description="Makes person a communist", help="communist [member]")
	async def _communist(self, ctx: commands.Context, member: commands.MemberConverter = None):
		async with ctx.typing():
			member = ctx.author if not member else member
			avatar = await member.avatar_url_as(format='png', size=1024).read()
			with io.BytesIO(avatar) as buff:
				avatar = Image.open(buff).resize((1000, 1000))
				flag = Image.open(
					self.assets + "pillow/communist.jpg").convert("RGBA")
				flag.putalpha(128)
				avatar.paste(flag, (0, 0), flag)
				final = io.BytesIO()
				avatar.save(final, format="PNG")
				final.seek(0)
				await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
							   embed=ImageEmbed(command="communist").Generate())

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
					font = ImageFont.truetype(
						self.assets + "fonts/Arial.ttf", 35)
					panWriter.text((410, 15), Utilities.Utilities.wrap(font=font, text="@{} dis you??".format(member.name), line_width=325),
								   font=font, fill="Black")
					pan.save(final, format="PNG")
					final.seek(0)
					await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
								   embed=ImageEmbed(command="ipan").Generate())

	@commands.command(name="presentation", description="Makes lisa simpson presentation meme with your text",
					  help="presentation <message> [member]")
	async def _presentation(self, ctx: commands.Context, *, message: str, member: commands.MemberConverter = None):
		async with ctx.typing():
			member = ctx.author if not member else member
			avatar = await member.avatar_url_as(format='png', size=1024).read()
			with io.BytesIO(avatar) as buff:
				avatar = Image.open(buff).resize((85, 75))
				presentation = Image.open(
					self.assets + "pillow/presentation.bmp")
				presentation.paste(avatar, (175, 280))
				final = io.BytesIO()
				presentationWriter = ImageDraw.Draw(presentation)
				font = ImageFont.truetype(self.assets + "fonts/Arial.ttf", 50)
				presentationWriter.text((120, 70), Utilities.wrap(font=font, text=message, line_width=450), font=font,
										fill="Black")
				presentation.save(final, format="PNG")
				final.seek(0)
				await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
							   embed=ImageEmbed(command="presentation").Generate())

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
				await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
							   embed=ImageEmbed(command="warned").Generate())

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
				baseWriter.text((30, 150), Utilities.wrap(font=font, text="@{} chillin".format(ctx.author.name), line_width=240),
								font=font, fill="Black")
				final = io.BytesIO()
				base.save(final, format="PNG")
				final.seek(0)
				await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
							   embed=ImageEmbed(command="menace").Generate())

	@commands.command(name="burn", description="Burns the specified text", help="burn <message>")
	async def _burn(self, ctx: commands.Context, *, message: str):
		burnit = Image.open(self.assets + "pillow/burnit.bmp")
		burnitWriter = ImageDraw.Draw(burnit)
		font = ImageFont.truetype(self.assets + "fonts/Arial.ttf", 50)
		burnitWriter.text((105, 185), Utilities.wrap(font, text=message,
										   line_width=365), font=font, fill="Black")
		final = io.BytesIO()
		burnit.save(final, format="PNG")
		final.seek(0)
		await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
					   embed=ImageEmbed(command="burn").Generate())

	@commands.command(name="match", description="Tinder match", help="match <lover1> [lover2]")
	async def _match(self, ctx: commands.Context, lover1: commands.MemberConverter,
					 lover2: commands.MemberConverter = None):
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
				await ctx.send(file=discord.File(final, filename=self.fileName + '.png'),
							   embed=ImageEmbed(command="match").Generate())

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
				gif[0].save(final, format='gif', save_all=True,
							append_images=gif[1:], loop=0, optimize=True)
				final.seek(0)
				await ctx.send(file=discord.File(final, filename=self.fileName + '.gif'),
							   embed=ImageEmbed(command="porno", extension=".gif").Generate())

	@commands.command(name="baby", description="bonk", help="baby <user>")
	async def _baby(self, ctx: commands.Context, user: commands.MemberConverter):
		async with ctx.typing():
			baby = user
			babyAvBytes = await baby.avatar_url_as(format="png", size=1024).read()
			with io.BytesIO(babyAvBytes) as babyAvIO:
				bonk = Image.open(self.assets + "pillow/bonk.gif")
				babyAv = Image.open(babyAvIO).resize((140, 170))
				gif = list()
				for i in range(0, bonk.n_frames):
					bonk.seek(i)
					frame = bonk.copy().convert('RGBA')
					frame.paste(babyAv, (350, 320), babyAv)
					gif.append(frame)
				final = io.BytesIO()
				gif[0].save(final, format='gif', save_all=True,
							append_images=gif[1:], loop=0, optimize=True)
				final.seek(0)
				await ctx.send(file=discord.File(final, filename=self.fileName + '.gif'),
							   embed=ImageEmbed(command="bonk", extension=".gif").Generate())


def setup(bot: commands.Bot):
	bot.add_cog(Images(bot))
