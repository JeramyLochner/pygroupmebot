from bottle import Bottle, run, route, request
from groupy import Group, Bot
import sys
import configparser
import random
import argparse
import subprocess

app = Bottle()

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--conf', help='Configuration file for bot and group', default='bot.ini', type=str)
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.conf)
botid = config['BOT']['id']
groupid = config['GROUP']['id']
botuserid = config['BOT']['user_id']

def runcommand(message):
	command = message.strip()
	process = subprocess.Popen(command.split()[1:], stdout=subprocess.PIPE)
	output, error = process.communicate()
	return str(output.replace("b'", "").replace("'", "").replace("\n", ""))[0:999]

message_replies = {'hello bot': ['Hi!', 'Hello!', 'Waddup'], '/test': 'test', '/command': runcommand}

@app.route('/', method='POST')
def listener():
	global botid, groupid, botuserid
	print(botid, " ", groupid, " ", botuserid)

	group, message = get_last_message(str(groupid))
	bot = get_bot(str(botid))
	print(message.user_id, "-", message)
	if message.user_id != botuserid:
		if message.text in message_replies:
			if callable(message_replies[message.text]):
				bot.post(message_replies[message.text](message.text))
			elif type(message_replies[message.text]) is list:
				bot.post(random.choice(message_replies[message.text]))
			else:
				bot.post(message_replies[message.text])
		else:
			command = message.text.split(' ')[0]
			print(command)
			if command in message_replies:
				if callable(message_replies[command]):
					bot.post(message_replies[command](message.text))

	return message

def get_last_message(groupid):
	groups = Group.list()
	for x in range(len(groups)):
		group = groups[x]
		if group.group_id == groupid:
			return group, group.messages().newest
	return group, group.messages().newest

def get_bot(botid):
	bots = Bot.list()
	for x in range(len(bots)):
		bot = bots[x]
		if bot.bot_id == botid:
			return bot

run(app, host="0.0.0.0", port=8080)
