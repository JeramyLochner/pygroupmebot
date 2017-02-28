from bottle import Bottle, run, route, request
from groupy import Group, Bot
import sys
import configparser
import random
import argparse
import subprocess
import random

app = Bottle()


class MarkovUser(object):

	def __init__(self, messages):
		self.cache = {}
		self.messages = messages
		self.messages_text = [message.text for message in messages]
		self.database()

	def triples(self):
		""" Generates triples from the given data string """
		for message in self.messages_text:
			if message == None:
				print("WTF")
			words = message.split()
			if len(words) < 3:
				self.messages_text.remove(message)
				continue
			for i in range(len(words)-3):
				yield (words[i], words[i+1], words[i+2])

	def database(self):
		for w1, w2, w3 in self.triples():
			key = (w1, w2, w3)
			if key in self.cache:
				self.cache[key].append(w3)
			else:
				self.cache[key] = [w3]

	def generate_markov_text(self, size=8):
		while True:
			seed_msg = random.choice([msg for msg in self.messages_text if len(msg) > 3])
			seed = random.randint(0, len(seed_msg)-3)
			seed_word, next_word = seed_msg[seed], seed_msg[seed+1]
			w1, w2 = seed_word, next_word

			gen_words = []
			try:
				for i in range(size):
					gen_words.append(w1)
					w1, w2 = w2, random.choice(self.cache[(w1, w2)])
				gen_words.append(w2)
			except KeyError:
				continue
			return ' '.join(gen_words).lower().title()


def runcommand(message):
	command = message.strip()
	process = subprocess.Popen(command.split()[1:], stdout=subprocess.PIPE)
	output, error = process.communicate()
	return str(output.replace("b'", "").replace("'", "").replace("\n", ""))[0:999]

def get_last_message(groupid):
	groups = Group.list()
	for x in range(len(groups)):
		group = groups[x]
		if group.group_id == groupid:
			return group, group.messages().newest
	return group, group.messages().newest

def get_all_messages(groupid):
	groups = Group.list()
	for x in range(len(groups)):
		group = groups[x]
		if group.group_id == groupid:
			messages = group.messages()
			while messages.iolder():
				pass
			print("Found {} messages in group {}".format(len(messages), groupid))
			return messages
	return None

def get_user_messages(messages, userid):
	usermsgs = []
	for msg in messages:
		if msg.user_id == userid:
			usermsgs.append(msg)
	return usermsgs

def get_bot(botid):
	bots = Bot.list()
	for x in range(len(bots)):
		bot = bots[x]
		if bot.bot_id == botid:
			return bot

@app.route('/', method='POST')
def listener():
	global botid, groupid, botuserid, all_messages
	print(botid, " ", groupid, " ", botuserid)

	group, message = get_last_message(str(groupid))
	bot = get_bot(str(botid))
	print(message.user_id, "-", message)

	if message.user_id != botuserid:
		usermsgs = get_user_messages(all_messages, message.user_id)
		userMarkov = MarkovUser(usermsgs)
		print(userMarkov.generate_markov_text(random.randint(3, 10)))

	return message

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--conf', help='Configuration file for bot and group', default='bot.ini', type=str)
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.conf)
botid = config['BOT']['id']
groupid = config['GROUP']['id']
botuserid = config['BOT']['user_id']

all_messages = get_all_messages("17007180")

run(app, host="0.0.0.0", port=8080)
