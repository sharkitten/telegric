import telepot

class TGBot(telepot.Bot):
	def __init__(self, config):
		self.singleMode = config['general']['single_mode'] == 'True'
		config = config['telegram']
		self.sender = config['sender']
		self.chatID = int(config['chatid'])
		self.bot = telepot.Bot(config['token'])
		self.users = set()
		#print(self.bot.getMe())

	def setIRCbot(self, bot):
		self.ircbot = bot

	def start(self):
		self.bot.message_loop(self.handle)

	def handle(self, msg):
		if (not self.ircbot.conn.is_connected()):
			self.ircbot.conn.connected_checker()
		print(msg)
		self.users.add(msg['from']['username'])
		if (msg['chat']['id']==self.chatID):
			self.ircbot.sendMessage(self.ircbot.channel, self.formatMessage(msg))
		else:
			print('message received from non-handled chat {} with ID {}'.format(msg['chat']['title'], msg['chat']['id']))

	def formatMessage(self, msg):
		try:
			body = msg['text']
		except KeyError:
			try:
				body = msg['sticker']['emoji']
			except KeyError:
				body = 'message type not supported'
		if self.singleMode:
			return body

		try:
			sender = msg['from'][self.sender]
		except:
			sender = msg['from']['first_name']
		return '<{}> {}'.format(sender, body)

	def send(self, msg):
		self.bot.sendMessage(self.chatID, msg)
