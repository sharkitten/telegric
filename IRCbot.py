import irc.bot
import sys


class IRCBot(irc.bot.SingleServerIRCBot):
    def __init__(self, config):
        """Set attributes from config file, start connection."""
        self.singleMode = config['general']['single_mode'] == 'True'
        config = config['irc']
        self.server = config['server']
        self.port = int(config['port'])
        self.nickname = config['nickname']
        self.channel = config['channel']
        irc.bot.SingleServerIRCBot.__init__(self, [(self.server, self.port)],
                                            self.nickname, self.nickname)
        self.register_handlers()

    def register_handlers(self):
        """Add handler methods for various IRC protocol events.

        Note that handlers of name 'on_' + event name are added automatically,
        so lines for 'nicknameinuse', 'privmsg', 'disconnect' would just add
        double handlers for on_nicknameinuse, on_privmsg, on_disconnect.
        """
        self.connection.add_global_handler('welcome', self.on_welcome)
        self.connection.add_global_handler('pubmsg', self.on_message)
        self.connection.add_global_handler('action', self.on_message)
        self.connection.add_global_handler('part', self.on_message)
        self.connection.add_global_handler('quit', self.on_message)
        self.connection.add_global_handler('join', self.on_message)
        self.connection.add_global_handler('topic', self.on_message)

    def on_nicknameinuse(self, c, e):
        """When nick is in use, reset it via NICK with '_' suffix added."""
        # TODO: What when nickname + _ grows beyond maximum allowed size?
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        """On IRC welcome event, join self.channel."""
        c.join(self.channel)

    def on_privmsg(self, conn, event):
        """When self.singleMode, format event to TGbot message, else deny."""
        if self.singleMode:
            self.TGbot.send(self.formatMessage(event))
        else:
            self.sendMessage(self.getNickname(event),
                             "I'm a bot. I have nothing to say.")

    def on_message(self, conn, event):
        """Format event to TGbot message."""
        self.TGbot.send(self.formatMessage(event))

    def formatMessage(self, msg):
        """Parse IRC message to TG message string.

        JOIN/PART messages become self.getNickname(msg) + 'joined'/'parted'
        strings.

        ACTION messages get a '/me' prefix, PRIVMSG messages a 'QUERY: ' one.
        String subpatterns that are in self.TGbot.users get a '@' prefix. All
        non-JOIN/PART messages thus created get a further <>-delimited
        self.getNickname(msg) prefix.
        """
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

        return '<{}> {}'.format(sender, body)

    def setTGbot(self, bot):
        """Set self.TGbot to bot, assuming it's an TGbot instance."""
        self.TGbot = bot

    def getNickname(self, event):
        return event.source.split('!')[0]

    def on_disconnect(self, c, e):
        """Reconnect client to IRC network."""
        self.connect()

    def sendMessage(self, recipient, msg):
        """Try sending msg to recipient via PRIVMSG, print error on failure."""
        try:
            self.connection.privmsg(recipient, msg)
        except Exception as e:
            sys.stderr.write(str(e) + '\n')
