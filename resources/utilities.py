# -*- coding: utf-8 -*-

import datetime
import logging
import sys
import traceback
import random
import string
import pprint
import pymysql.cursors
from dotenv import load_dotenv
import os

load_dotenv(".env")

databaseConfig = pymysql.connect(
	host=os.getenv("mysqlServer"),
	user="root",
	password=os.getenv("mysqlPassword"),
	port=3306,
	database="tragedy",
	charset='utf8mb4',
	cursorclass=pymysql.cursors.DictCursor,
	read_timeout=5,
	write_timeout=5,
	connect_timeout=5,
	autocommit=True
	)

class Utilities():
	def __init__(self, bot):
		self.bot = bot

def dotenvVar(var: str):
	load_dotenv('.env')
	return os.getenv(var)

def EmojiBool(bool: bool):
	switch = {
		True: ":white_check_mark:",
		False: ":x:",
	}
	return switch.get(bool, "N/A")

def humansize(nbytes): #https://stackoverflow.com/questions/14996453/python-libraries-to-calculate-human-readable-filesize-from-bytes
	suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
	i = 0
	while nbytes >= 1024 and i < len(suffixes)-1:
		nbytes /= 1024.
		i += 1
	f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
	return '%s %s' % (f, suffixes[i])

def humanStatus(status):
	switch = {
		"dnd": "Do Not Disturb.",
		"online": "Online.",
		"idle": "Idle.",
		"offline": "Offline.",
	}
	return switch.get(status, "Error.")

def custom_prefix(bot, message):
	try:
		cursor = databaseConfig.cursor()
		cursor.execute("SELECT * FROM prefix WHERE guild=%s", (str(message.guild.id)))
		return cursor.fetchone().get("prefix")
	except AttributeError as exc:
		try:
			cursor.execute("INSERT INTO prefix (guild, prefix) VALUES (%s, 'xv ')", (str(message.guild.id)))
			databaseConfig.commit()
			print("[Logging] Added {} ({}) to prefix database.".format(message.guild.name, str(message.guild.id)))
		except Exception as exc:
			logError(exc)
	except pymysql.err.InterfaceError as exc:
			logError(exc)

def randomString(length):
	components = string.ascii_lowercase
	randString = ''.join(random.choice(components) in range(length))
	return randString

def logError(exception: Exception):
	exc_type, exc_value, exc_tb = sys.exc_info()
	exception = traceback.format_exception(exc_type, exc_value, exc_tb)
	debugFile = open('./debug/exceptions.log', 'w')
	pprint.pprint(exception, stream=debugFile)
	debugFile.close()
	logging.log(logging.ERROR, "Exception was thrown, to see more details open /debug/exceptions.log")

while __name__ == "__main__":
	try:
		databaseConfig.ping(reconnect=False)
	except Exception as exc:
		logging.log(logging.CRITICAL, exc)
		logging.log(logging.INFO, "Attempting to reconnect to MySQL database in '{}'".format(__file__[:-3]))
		databaseConfig = pymysql.connect(
			host=os.getenv("mysqlServer"),
			user="root",
			password=os.getenv("mysqlPassword"),
			port=3306,
			database="tragedy",
			charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor,
			read_timeout=5,
			write_timeout=5,
			connect_timeout=5,
			autocommit=True
			)