from discord.ext import commands


class NotVoter(commands.CheckFailure):
	pass

class WelcomeNotConfigured(commands.CheckFailure):
    pass

class ShopItem(object):
    def __init__(self, item_name, item_price, item_emoji):
        self.name = item_name
        self.price = item_price
        self.emoji = item_emoji
