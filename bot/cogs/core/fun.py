# -*- coding: utf-8 -*-

import asyncio
import hashlib
import random
import re
import string
import json
import contextlib
import typing

import aiohttp
import discord
from discord.colour import Color
from discord.errors import InvalidArgument
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.errors import BadArgument
from discord_components import *


class Fun(commands.Cog, description="Fun commands to make discord just a bit better !"):
	def __init__(self, bot):
		self.bot = bot
		self.aiohttp = aiohttp.ClientSession()
		DiscordComponents(bot)

	@commands.command(description="Searches for specified phrase on urbandictionary.com", help="urban <phrase>")
	@commands.cooldown(1, 5, type=BucketType.member)
	async def urban(self, ctx, *, phrase):
		async with self.aiohttp.get("http://api.urbandictionary.com/v0/define?term={}".format(phrase)) as urb:
			urban = await urb.json()
			try:
				embed = discord.Embed(
					title=f"Term - \"{phrase}\"", color=discord.Color.green())
				embed.add_field(name="Definition",
				                value=urban['list'][0]['definition'].replace('[', '').replace(']', ''))
				embed.add_field(name="Example", value=urban['list'][0]['example'].replace(
					'[', '').replace(']', ''))
				temp = await ctx.reply(embed=embed, mention_author=True)
				await asyncio.sleep(15)
				await temp.delete()
				await ctx.message.delete()
			except:
				pass

	@commands.command(description="Finds synonym(s) for the specified word", help="synonym <word>")
	@commands.cooldown(1, 5, type=BucketType.member)
	async def synonym(self, ctx: commands.Context, *, word: str):
		async with self.aiohttp.get("https://word-simi.herokuapp.com/api/v1/most_similar/{}?count=5".format(word)) as x:
			parse = await x.json()
			embed = discord.Embed(title="Synonyms", description="Synonyms for the word \"{}\"".format(word),
			                      color=Color.green())
			for _index in range(len(parse["result"])):
				embed.add_field(
					name='\u200b', value="**{}**".format(parse["result"][_index]["word"]), inline=False)
			await ctx.send(embed=embed)

	@commands.command(description="Shortens specified url with 3 different url shorteners", help="shorten <url>")
	@commands.cooldown(1, 5, type=BucketType.member)
	async def shorten(self, ctx: commands.Context, *, url: str):
		async with ctx.typing():
			embed = discord.Embed(
				title="URL Shortener ({})".format(url), color=Color.green())
			async with self.aiohttp.get("https://api.shrtco.de/v2/shorten?url={}".format(url)) as shrtco:
				async with self.aiohttp.get("https://clck.ru/--?url={}".format(url)) as clck:
					async with self.aiohttp.get("http://tinyurl.com/api-create.php?url={}".format(url)) as tiny:
						parse = await shrtco.json()
						embed.add_field(name="Shortened URL (9qr.de)", value=parse["result"]["full_short_link2"],
						                inline=False)
						embed.add_field(name="Shortened URL (clck.ru)", value=await clck.text(), inline=False)
						embed.add_field(name="Shortened URL (tinyurl.com)", value=await tiny.text(), inline=False)
		await ctx.reply(embed=embed, mention_author=True)

	@commands.command(aliases=["guessgame", "smiley", "find"], description="Find the smiley face game", help="guess")
	@commands.cooldown(1, 5, BucketType.member)
	async def guess(self, ctx):
		probabilityList = ["||:bomb:||", "||:smiley:||", "||:bomb:||", "||:bomb:||", "||:bomb:||", "||:bomb:||",
		                   "||:bomb:||", "||:bomb:||", "||:bomb:||", "||:bomb:||"]
		random.shuffle(probabilityList)
		embed = discord.Embed(color=discord.Colour.red(), title="Find The Smiley !",
		                      description=' '.join(probabilityList))
		await ctx.send(embed=embed)

	@commands.command(description="Porn", help="nsfw <type>")
	@commands.is_nsfw()
	@commands.cooldown(1, 3, type=BucketType.member)
	async def nsfw(self, ctx, *, type: str):
		with open("bot/assets/json/nsfw.json", "r") as urls:
			with contextlib.suppress(KeyError):
				jObj = json.load(urls)
				query = jObj[type.replace(' ', '_')]
				async with aiohttp.ClientSession() as requests:
					async with requests.get("https://scathach.redsplit.org/v3{}".format(query)) as response:
						data = await response.json()
						_url = data["url"]
						embed = discord.Embed(title=type.title(), description="Take this weirdo",
						                      color=Color.green()).set_image(url=_url)
						await ctx.reply(embed=embed, mention_author=True)


	@commands.command(aliases=["bubbles", "wrap", "pop"], description="It's just bubble wrap", help="bubblewrap")
	@commands.cooldown(1, 5, BucketType.member)
	async def bubblewrap(self, ctx):
		wrap = ("||:boom:|| " * 9 + '\r\n') * 9
		embed = discord.Embed(title="Bubble Wrap !",
		                      description=wrap, color=Color.green())
		await ctx.send(embed=embed)

	@commands.command(name="rr?", description="Detects if provided url is a rick-roll", help="rr? <url>")
	async def _rr(self, ctx: commands.Context, *, url: str):
		if not re.match(discord.utils._URL_REGEX, url):
			raise BadArgument("Invalid URL")

		phrases = ["rickroll", "rick roll", "rick astley", "never gonna give you up"]
		source = str(await (await self.aiohttp.get(url, allow_redirects=True)).content.read()).lower()
		rickRoll = bool((re.findall('|'.join(phrases), source, re.MULTILINE | re.IGNORECASE)))
		await ctx.reply(embed=discord.Embed(
			title="Rick Roll {} in webpage".format("was found" if rickRoll is True else "was not found"),
			color=Color.red() if rickRoll is True else Color.green(),
		), mention_author=True)

	@commands.command(name="hash", description="Hashes provided text with provided algorithm",
	                  help="hash <algorithm> <message>")
	@commands.cooldown(1, 5, BucketType.member)
	async def _hash(self, ctx, algorithm: str, *, message):
		algos: dict[str, str] = {
			"md5": hashlib.md5(bytes(message.encode("utf-8"))).hexdigest(),
			"sha1": hashlib.sha1(bytes(message.encode("utf-8"))).hexdigest(),
			"sha224": hashlib.sha224(bytes(message.encode("utf-8"))).hexdigest(),
			"sha3_224": hashlib.sha3_224(bytes(message.encode("utf-8"))).hexdigest(),
			"sha256": hashlib.sha256(bytes(message.encode("utf-8"))).hexdigest(),
			"sha3_256": hashlib.sha3_256(bytes(message.encode("utf-8"))).hexdigest(),
			"sha384": hashlib.sha384(bytes(message.encode("utf-8"))).hexdigest(),
			"sha3_384": hashlib.sha3_384(bytes(message.encode("utf-8"))).hexdigest(),
			"sha512": hashlib.sha512(bytes(message.encode("utf-8"))).hexdigest(),
			"sha3_512": hashlib.sha3_512(bytes(message.encode("utf-8"))).hexdigest(),
			"blake2b": hashlib.blake2b(bytes(message.encode("utf-8"))).hexdigest(),
			"blake2s": hashlib.blake2s(bytes(message.encode("utf-8"))).hexdigest()
		}
		embed = discord.Embed(color=Color.green(),
		                      title="Hashed \"{}\"".format(message))
		if algorithm.lower() not in list(algos.keys()):
			for algo in list(algos.keys()):
				hashValue = algos[algo]
				embed.add_field(name=algo, value="```{}```".format(hashValue))
		else:
			embed.add_field(name=algorithm, value="```{}```".format(
				algos[algorithm.lower()]), inline=False)
		await ctx.reply(embed=embed, mention_author=True)


def setup(bot):
	bot.add_cog(Fun(bot))
