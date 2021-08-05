# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
import DiscordUtils

class Music(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.music = DiscordUtils.Music()

	@commands.command()
	async def join(self, ctx):
		await ctx.author.voice.channel.connect()
	
	@commands.command()
	async def leave(self, ctx):
		await ctx.voice_client.disconnect()
	
	@commands.command()
	async def play(self, ctx, *, url):
		player = self.music.get_player(guild_id=ctx.guild.id)
		if not player:
			player = self.music.create_player(ctx, ffmpeg_error_betterfix=True)
		if not ctx.voice_client.is_playing():
			await player.queue(url, search=True)
			song = await player.play()
			await ctx.send(f"Playing {song.name}")
		else:
			song = await player.queue(url, search=True)
			await ctx.send(f"Queued {song.name}")
	
	@commands.command()
	async def pause(self, ctx):
		player = self.music.get_player(guild_id=ctx.guild.id)
		song = await player.pause()
		await ctx.send(f"Paused {song.name}")
	
	@commands.command()
	async def resume(self, ctx):
		player = self.music.get_player(guild_id=ctx.guild.id)
		song = await player.resume()
		await ctx.send(f"Resumed {song.name}")
	
	@commands.command()
	async def stop(self, ctx):
		player = self.music.get_player(guild_id=ctx.guild.id)
		await player.stop()
		await ctx.send("Stopped")
	
	@commands.command()
	async def loop(self, ctx):
		player = self.music.get_player(guild_id=ctx.guild.id)
		song = await player.toggle_song_loop()
		if song.is_looping:
			await ctx.send(f"Enabled loop for {song.name}")
		else:
			await ctx.send(f"Disabled loop for {song.name}")
	
	@commands.command()
	async def queue(self, ctx):
		player = self.music.get_player(guild_id=ctx.guild.id)
		await ctx.send(f"{', '.join([song.name for song in player.current_queue()])}")
	
	@commands.command()
	async def np(self, ctx):
		player = self.music.get_player(guild_id=ctx.guild.id)
		song = player.now_playing()
		await ctx.send(song.name)
	
	@commands.command()
	async def skip(self, ctx):
		player = self.music.get_player(guild_id=ctx.guild.id)
		data = await player.skip(force=True)
		if len(data) == 2:
			await ctx.send(f"Skipped from {data[0].name} to {data[1].name}")
		else:
			await ctx.send(f"Skipped {data[0].name}")
	
	@commands.command()
	async def volume(self, ctx, vol):
		player = self.music.get_player(guild_id=ctx.guild.id)
		song, volume = await player.change_volume(float(vol) / 100) # volume should be a float between 0 to 1
		await ctx.send(f"Changed volume for {song.name} to {volume*100}%")
	
	@commands.command()
	async def remove(self, ctx, index):
		player = self.music.get_player(guild_id=ctx.guild.id)
		song = await player.remove_from_queue(int(index))
		await ctx.send(f"Removed {song.name} from queue")

def setup(bot):
	bot.add_cog(Music(bot))
