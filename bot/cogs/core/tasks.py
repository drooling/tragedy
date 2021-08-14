import discord
import asyncio
import pprint
from discord.ext import commands, tasks
import pymysql.cursors
import bot.utils.utilities as tragedy


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mysqlPing.start()
        self.pool = pymysql.connect(
	        host=tragedy.DotenvVar("mysqlServer"),
	        user="root",
	        password=tragedy.DotenvVar("mysqlPassword"),
	        port=3306,
	        database="tragedy",
	        charset='utf8mb4',
	        cursorclass=pymysql.cursors.DictCursor,
	        read_timeout=5,
	        write_timeout=5,
	        connect_timeout=5,
	        autocommit=True
        )

    @tasks.loop(seconds=35)
    async def mysqlPing(self):
    	connected = bool(self.pool.open)
    	pprint.pprint(
    		"Testing connection to mysql database () --> {}".format(str(connected).upper()))
    	if connected is False:
    		self.pool.ping(reconnect=True)
    		pprint.pprint("Reconnecting to database () --> SUCCESS")
    	else:
    		pass

def setup(bot: commands.Bot):
    bot.add_cog(Tasks(bot))