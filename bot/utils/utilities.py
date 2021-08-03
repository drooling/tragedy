# -*- coding: utf-8 -*-
import logging
import os
import pprint
import random
import string
import sys
import traceback

import pymysql.cursors
from dotenv import load_dotenv

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


def DotenvVar(var: str):
	load_dotenv('.env')
	return os.getenv(var)


def EmojiBool(bool: bool):
	switch = {
		True: ":white_check_mark:",
		False: ":x:",
	}
	return switch.get(bool, "N/A")


def HumanStatus(status):
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
		return ["xv ", cursor.fetchone().get("prefix")]
	except AttributeError as exc:
		try:
			cursor.execute("INSERT INTO prefix (guild, prefix) VALUES (%s, 'xv ')", (str(message.guild.id)))
			databaseConfig.commit()
			print("[Logging] Added {} ({}) to prefix database.".format(message.guild.name, str(message.guild.id)))
		except Exception as exc:
			logError(exc)
	except pymysql.err.InterfaceError as exc:
		logError(exc)


def logError(exception: Exception):
	logging.log(logging.ERROR, exception)
	traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

def logInfo(message):
	logging.log(logging.INFO, message)

def wrap(font, text,
         line_width):  # https://github.com/DankMemer/imgen/blob/master/utils/textutils.py (useful asf so i stole it not even gonna cap w you)
	words = text.split()
	lines = []
	line = []
	for word in words:
		newline = ' '.join(line + [word])
		width, height = font.getsize(newline)
		if width > line_width:
			lines.append(' '.join(line))
			line = [word]
		else:
			line.append(word)
	if line:
		lines.append(' '.join(line))
	return ('\n'.join(lines)).strip()


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
