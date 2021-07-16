# -*- coding: utf-8 -*-

import os
from discord.colour import Color
from discord.ext import commands
import discord
import asyncio
import aiohttp
from discord.ext.commands.cooldowns import BucketType
import random
import io


class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.aiohttp = aiohttp.ClientSession()

	@commands.command()
	@commands.cooldown(1, 5, type=BucketType.member)
	async def urban(self, ctx, *, phrase):
		async with aiohttp.ClientSession() as requests:
			async with requests.get("http://api.urbandictionary.com/v0/define?term={}".format(phrase)) as urb:
				urban = await urb.json()
				try:
					embed = discord.Embed(title=f"Term - \"{phrase}\"", color=discord.Color.green())
					embed.add_field(name="Definition", value=urban['list'][0]['definition'].replace('[', '').replace(']', ''))
					embed.add_field(name="Example", value=urban['list'][0]['example'].replace('[', '').replace(']', ''))
					temp = await ctx.reply(embed=embed, mention_author=True)
					await asyncio.sleep(15)
					await temp.delete()
					await ctx.message.delete()
				except:
					pass

	@commands.command()
	@commands.cooldown(1, 5, type=BucketType.member)
	async def synonym(self, ctx:commands.Context, *, word: str):
		async with self.aiohttp.get("https://word-simi.herokuapp.com/api/v1/most_similar/{}?count=5".format(word)) as x:
			parse = await x.json()
			embed=discord.Embed(title="Synonyms", description="Synonyms for the word \"{}\"".format(word), color=Color.green())
			for _index in range(len(parse["result"])):
				embed.add_field(name="\u200b", value="**{}**".format(parse["result"][_index]["word"]), inline=False)
			await ctx.send(embed=embed)

	@commands.command()
	@commands.cooldown(1, 5, type=BucketType.member)
	async def shorten(self, ctx:commands.Context, *, url: str):
		embed=discord.Embed(title="URL Shortener ({})".format(url), color=Color.green())
		async with self.aiohttp.get("https://api.shrtco.de/v2/shorten?url={}".format(url)) as x:
			parse = await x.json()
			embed.add_field(name="Shortened URL (9qr.de)", value=parse["result"]["full_short_link2"], inline=False)
		async with self.aiohttp.get("https://clck.ru/--?url={}".format(url)) as x:
			embed.add_field(name="Shortened URL (clck.ru)", value=await x.text(), inline=False)
		async with self.aiohttp.get("http://tinyurl.com/api-create.php?url={}".format(url)) as x:
			embed.add_field(name="Shortened URL (tinyurl.com)", value=await x.text(), inline=False)
		await ctx.reply(embed=embed, mention_author=True)

	@commands.command(aliases=["deepfry", "deepfried"])
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

	@commands.command()
	@commands.cooldown(1, 5, BucketType.member)
	async def obama(self, ctx, *, message: str):
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

	@commands.command(aliases=["guessgame", "smiley", "find"])
	@commands.cooldown(1, 5, BucketType.member)
	async def guess(self, ctx):
		probabilityList = ["||:bomb:||", "||:smiley:||", "||:bomb:||", "||:bomb:||", "||:bomb:||", "||:bomb:||", "||:bomb:||", "||:bomb:||", "||:bomb:||", "||:bomb:||"]
		random.shuffle(probabilityList)
		embed = discord.Embed(color=discord.Colour.red(), title="Find The Smiley !", description=' '.join(probabilityList))
		await ctx.send(embed=embed)

	@commands.command(aliases=["bubbles", "wrap", "pop"])
	@commands.cooldown(1, 5, BucketType.member)
	async def bubblewrap(self, ctx):
		wrap = ("||:boom:|| " * 9 + '\n') * 9
		embed=discord.Embed(title="Bubble Wrap !", description=wrap, color=Color.green())
		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Fun(bot))
