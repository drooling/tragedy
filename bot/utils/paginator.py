import asyncio
import asyncio.exceptions

SkipPrevious = "\u23EA"
Previous = "\u25C0"
End = "\u274C"
Next = "\u25B6"
SkipNext = "\u23E9"

EMOJIS = [SkipPrevious, Previous, End, Next, SkipNext]


class Paginator:
	def __init__(self, bot, ctx, pages, timeout=30):
		self.bot = bot
		self.ctx = ctx
		self.pages = pages
		self.timeout = timeout

		self.index = int()
		self.paginating = True

		self.func = None
		self.emoji_handler = {
			SkipPrevious: self.skip_previous,
			Previous: self.previous,
			End: self.session_end,
			Next: self.next,
			SkipNext: self.skip_next
		}

	async def skip_previous(self):
		self.index = 0

	async def skip_next(self):
		self.index = len(self.pages) - 1

	async def next(self):
		if self.index != len(self.pages) - 1:
			self.index += 1

	async def previous(self):
		if self.index != 0:
			self.index -= 1

	async def session_end(self):
		self.paginating = False
		await self.message.clear_reactions()

	def check(self, reaction, user):
		if reaction.emoji in EMOJIS:
			self.func = self.emoji_handler[reaction.emoji]
		return (user == self.ctx.message.author and self.message.id == reaction.message.id and reaction.emoji in EMOJIS)

	async def run(self):
		self.pages[self.index].set_footer(text="{}/{}".format(self.index + 1, len(self.pages)))
		self.message = await self.ctx.send(embed=self.pages[self.index])

		for emoji in EMOJIS:
			await self.message.add_reaction(emoji)

		while self.paginating:
			try:
				await self.wait_first(self.on_reaction_add(), self.on_reaction_remove())
			except TimeoutError:
				await self.session_end()
				self.pages[self.index].set_footer(text=f"Session Ended.")
				await self.message.edit(embed=self.pages[self.index])
			else:
				await self.func()
				if self.paginating:
					self.pages[self.index].set_footer(text="{}/{}".format(self.index + 1, len(self.pages)))
					await self.message.edit(embed=self.pages[self.index])
				else:
					self.pages[self.index].set_footer(text=f"Session Ended.")
					await self.message.edit(embed=self.pages[self.index])

	async def wait_first(self, *futures):
		done, pending = await asyncio.wait(futures, return_when=asyncio.FIRST_COMPLETED)
		gather = asyncio.gather(*pending)
		gather.cancel()
		try:
			await gather
		except asyncio.exceptions.CancelledError:
			pass
		return done.pop().result()

	async def on_reaction_add(self):
		try:
			return await self.bot.wait_for("reaction_add", check=self.check, timeout=self.timeout)
		except asyncio.exceptions.TimeoutError:
			await self.session_end()

	async def on_reaction_remove(self):
		try:
			return await self.bot.wait_for("reaction_remove", check=self.check, timeout=self.timeout)
		except asyncio.exceptions.TimeoutError:
			await self.session_end()
