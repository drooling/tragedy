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

class AutoModConfig(object):
    def __init__(self, profanity_filter: bool, link_filter: bool, mention_filter: bool, mention_length: int, spam_filter: bool, spam_ratio: tuple):
        self.profanity_filter = profanity_filter
        self.link_filter = link_filter
        self.mention_filter = mention_filter
        self.mention_length = mention_length
        self.spam_filter = spam_filter
        self.spam_ratio = spam_ratio