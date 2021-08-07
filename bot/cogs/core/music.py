# -*- coding: utf-8 -*-

import asyncio
import random
import humanize

from discord.colour import Color
from bot.utils.utilities import EmojiBool
from discord.ext import commands
import discord
import DiscordUtils
import youtube_dl

class Music(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.music = DiscordUtils.Music()

	@commands.command()
	async def join(self, ctx):
		if not ctx.author.voice or not ctx.author.voice.channel:
			return await ctx.send('❌ **You are not connected to any voice channel**')
		destination = ctx.author.voice.channel
		await destination.connect()
		await ctx.send("✅ **Joined voice channel** `{}`".format(ctx.author.voice.channel))
	
	@commands.command()
	async def leave(self, ctx):
		await ctx.voice_client.disconnect()
		await ctx.send("✅ **Left voice channel** `{}`".format(ctx.author.voice.channel))
	
	@commands.command()
	async def play(self, ctx, *, url):
		player = self.music.get_player(guild_id=ctx.guild.id)
		if not player:
			player = self.music.create_player(ctx, ffmpeg_error_betterfix=True)
		if not ctx.voice_client.is_playing():
			await ctx.send("**Searching YouTube**")
			await player.queue(url, search=True, bettersearch=True)
			song = await player.play()
			await ctx.send("**Now playing 🎶** `{}`".format(song.name))
		else:
			song = await player.queue(url, search=True)
			await ctx.send("✅ **Queued** `{}`".format(song.name))
	
	@commands.command()
	async def pause(self, ctx):
		player = self.music.get_player(guild_id=ctx.guild.id)
		song = await player.pause()
		await ctx.send("✅ **Paused** `{}`".format(song.name))
	
	@commands.command()
	async def resume(self, ctx):
		player = self.music.get_player(guild_id=ctx.guild.id)
		song = await player.resume()
		await ctx.send("✅ **Resumed** `{}`".format(song.name))
	
	@commands.command()
	async def stop(self, ctx):
		player = self.music.get_player(guild_id=ctx.guild.id)
		await player.stop()
		await ctx.send("Stopped")
	
	@commands.command()
	async def loop(self, ctx):
		player = self.music.get_player(guild_id=ctx.guild.id)
		try:
			song = await player.toggle_song_loop()
		except DiscordUtils.NotPlaying:
			return await ctx.send("❌ **Nothing is playing**")
		if song.is_looping:
			await ctx.send("🔂 **Loop enabled** - `{}`".format(song.name))
		else:
			await ctx.send("🔂 **Loop disabled** - `**{}**`".format(song.name))
	
	@commands.command()
	async def queue(self, ctx):
		player = self.music.get_player(guild_id=ctx.guild.id)
		await ctx.send('**' + '**\n**'.join([song.name for song in player.current_queue()]) + '**')
	
	@commands.command()
	async def np(self, ctx):
		player = self.music.get_player(guild_id=ctx.guild.id)
		song = player.now_playing()
		embed = (discord.Embed(title='Now playing', description='```%s```' % (song.name), color=Color.green())
				.add_field(name='Views', value=humanize.intword(song.views), inline=False)
				.add_field(name='Duration', value=humanize.naturaldelta(song.duration))
				.add_field(name='Loop?', value=EmojiBool(song.is_looping))
				.add_field(name='YouTube URL', value='[Click Here](%s)' % (song.url), inline=False)
				.add_field(name='Uploader YouTube Channel', value='[%s](%s)' % (song.channel, song.channel_url))
				.set_thumbnail(url=song.thumbnail))
		await ctx.send(embed=embed)

	@commands.command(name='shuffle')
	async def _shuffle(self, ctx: commands.Context):
		player = self.music.get_player(guild_id=ctx.guild.id)

		if len(player.current_queue()) == 0:
			return await ctx.send('❌ **Empty queue**')

		random.shuffle(player.current_queue())
		await ctx.send('✅ **Shuffled queue**')
	
	@commands.command()
	async def skip(self, ctx):
		player = self.music.get_player(guild_id=ctx.guild.id)
		song = player.now_playing()
		await player.skip(force=True)
		await ctx.send("✅ **Skipped** `{}`".format(song.name))
		song = player.now_playing()
		await ctx.send("**Now playing** `{}`".format(song.name))
	
	@commands.command()
	async def volume(self, ctx, volume: int):
		player = self.music.get_player(guild_id=ctx.guild.id)
		old_volume = ctx.voice_client.source.volume
		song, volume = await player.change_volume(float(volume) / 100)
		if volume > old_volume:
			await ctx.send("🔊 **Changed volume for** `{}` **to** `{}%`".format(song.name, int(volume * 100)))
		elif volume < old_volume:
			await ctx.send("🔉 **Changed volume for** `{}` **to** `{}%`".format(song.name, int(volume * 100)))
	
	@commands.command()
	async def remove(self, ctx, index):
		player = self.music.get_player(guild_id=ctx.guild.id)
		song = await player.remove_from_queue(int(index))
		await ctx.send("✅ **Removed** `%s` **from queue**" % (song.name))

def setup(bot):
	bot.add_cog(Music(bot))
