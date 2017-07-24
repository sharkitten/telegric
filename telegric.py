import configparser
import TGBot
import IRCbot
import threading
import time

if __name__ == '__main__':
    config = configparser.SafeConfigParser()
    config.read('config')

    telegram = TGBot.TGBot(config)
    irc = IRCbot.IRCBot(config)

    telegram.setIRCbot(irc)
    irc.setTGbot(telegram)

    thread1 = threading.Thread(target=telegram.start, args=())
    thread2 = threading.Thread(target=irc.start, args=())

    thread1.daemon = True
    thread1.start()
    thread2.daemon = True
    thread2.start()

    while True:
        time.sleep(30)
        if (not irc.conn.is_connected()):
            irc.connect()
