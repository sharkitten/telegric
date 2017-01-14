#! /usr/bin/env python

import irc.bot
import sys
import irc.strings

class IRCBot(irc.bot.SingleServerIRCBot):
	def __init__(self, config):
		self.singleMode = config['general']['single_mode'] == 'True'
		config = config['irc']
		self.server = config['server']
		self.port = int(config['port'])
		self.nickname = config['nickname']
		self.client = irc.bot.SingleServerIRCBot([(self.server, self.port)], self.nickname, self.nickname)
		self.channel = config['channel']
		self.conn = self.client.connection
		self.reconnection_interval = 60

	def register_handlers(self):
		self.conn.add_global_handler('welcome', self.on_welcome)
		self.conn.add_global_handler('nicknameinuse', self.on_nicknameinuse)
		self.conn.add_global_handler('privmsg', self.on_privmsg)
		self.conn.add_global_handler('pubmsg', self.on_message)
		self.conn.add_global_handler('action', self.on_message)
		self.conn.add_global_handler('part', self.on_message)
		self.conn.add_global_handler('quit', self.on_message)
		self.conn.add_global_handler('join', self.on_message)
		self.conn.add_global_handler('topic', self.on_message)
		self.conn.add_global_handler('disconnect', self.on_disconnect)


#        for i in ["disconnect", "join", "kick", "mode",
#                  "namreply", "nick", "part", "quit"]:
#            self.connection.add_global_handler(i,
#                                               getattr(self, "_on_" + i),
#                                               -10)

	def start(self):
		self.register_handlers()
		self.client.start()

	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")

	def on_welcome(self, c, e):
		c.join(self.channel)

	def on_privmsg(self, conn, event):
		if self.singleMode:
			self.TGbot.send(self.formatMessage(event))
		else:
			self.sendMessage(self.getNickname(event), "I'm a bot. I have nothing to say.")

	def on_message(self, conn, event):
		self.TGbot.send(self.formatMessage(event))

	def formatMessage(self, msg):
		sender = self.getNickname(msg)
		body = ''.join(msg.arguments)
		type = msg.type

		if type == 'action':
			body = '/me ' + body
		elif type == 'privmsg':
			body = 'QUERY: ' + body
		elif type == 'join':
			return '{} joined'.format(self.getNickname(msg))
		elif type == 'part' or type == 'quit':
			return '{} left'.format(self.getNickname(msg))

		for user in self.TGbot.users:
			body = str.replace(body, user, '@'+user)

		return '<{}> {}'.format(sender, body)

	def setTGbot(self, bot):
	    self.TGbot = bot

	def getNickname(self, event):
		return event.source.split('!')[0]

	def on_disconnect(self, c, e):
		print("disconnected")
		self.connect()

	def connect(self):
		#self.conn.connect(self.server, self.port,self.nickname)
		self.client.connect()

	def sendMessage(self, recipient, msg):
		try:
			self.conn.privmsg(recipient, msg)
		except Exception as e:
			sys.stderr.write(str(e) + '\n')
