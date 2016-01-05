#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

import sys
import logging
import getpass
from optparse import OptionParser
from time import gmtime, strftime
from datetime import datetime
import json
from urlhandler import URLHandler
from lastseen import LastSeen
from google import Google
from dice import Dice

import re

import sleekxmpp


XMPP_CA_CERT_FILE = None

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


class MUCBot(sleekxmpp.ClientXMPP):

    """
    A simple SleekXMPP bot that will greets those
    who enter the room, and acknowledge any messages
    that mentions the bot's nickname.
    """

    def __init__(self, jid, password, room, nick):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        
        self.plugins = [URLHandler(self), LastSeen(self), Google(self), Dice(self)]

        self.room = room
        self.nick = nick

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The groupchat_message event is triggered whenever a message
        # stanza is received from any chat room. If you also also
        # register a handler for the 'message' event, MUC messages
        # will be processed by both handlers.
        self.add_event_handler("groupchat_message", self.muc_message)

        # The groupchat_presence event is triggered whenever a
        # presence stanza is received from any chat room, including
        # any presences you send yourself. To limit event handling
        # to a single room, use the events muc::room@server::presence,
        # muc::room@server::got_online, or muc::room@server::got_offline.
        self.add_event_handler("muc::%s::got_online" % self.room,
                               self.muc_online)

        self.logfile = datetime.strftime(datetime.now(), "logs/%Y%m%d_%H%M.txt")
        self.urlfile = datetime.strftime(datetime.now(), "logs/urls.txt")
        self.logfile_handle = open(self.logfile, "w")
        self.urlfile_handle = open(self.logfile, "a")

        self.urls = [] #todo: read file

    def log(self, msg):
        timestamp = strftime("[%Y-%m-%d %H:%M:%S +0000]", gmtime())
        log = { "timestamp" : timestamp,
                "nick" : str(msg['from']),
                "body" : str(msg['body'])}

        self.logfile_handle.write(json.dumps(log))
        self.logfile_handle.write("\n")
        self.logfile_handle.flush()


    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.get_roster()
        self.send_presence()
        self.plugin['xep_0045'].joinMUC(self.room,
                                        self.nick,
                                        # If a room password is needed, use:
                                        # password=the_room_password,
                                        wait=True)

    def muc_message(self, msg):
        """
        Process incoming message stanzas from any chat room. Be aware
        that if you also have any handlers for the 'message' event,
        message stanzas may be processed by both handlers, so check
        the 'type' attribute when using a 'message' event handler.

        Whenever the bot's nickname is mentioned, respond to
        the message.

        IMPORTANT: Always check that a message is not from yourself,
                   otherwise you will create an infinite loop responding
                   to your own messages.

        This handler will reply to messages that mention
        the bot's nickname.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
#        if msg['mucnick'] != self.nick and self.nick in msg['body']:
#            self.send_message(mto=msg['from'].bare,
#                              mbody="I heard that, %s." % msg['mucnick'],
#                              mtype='groupchat')



        #disabled because simon whines
        #self.log(msg)
        for p in self.plugins:
            p.handle(msg)


    def muc_online(self, presence):
        """
        Process a presence stanza from a chat room. In this case,
        presences from users that have just come online are
        handled by sending a welcome message that includes
        the user's nickname and role in the room.

        Arguments:
            presence -- The received presence stanza. See the
                        documentation for the Presence stanza
                        to see how else it may be used.
        """
#        if presence['muc']['nick'] != self.nick:
#            self.send_message(mto=presence['from'].bare,
#                              mbody="Hello, %s %s" % (presence['muc']['role'],
#                                                      presence['muc']['nick']),
#                              mtype='groupchat')


if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-r", "--room", dest="room",
                    help="MUC room to join")
    optp.add_option("-n", "--nick", dest="nick",
                    help="MUC nickname")

	# Proxy
    optp.add_option("--proxy-host", dest="proxy_host",
                    help="Proxy host")
    optp.add_option("--proxy-port", dest="proxy_port",
                    help="Proxy port")
    optp.add_option("--proxy-username", dest="proxy_username",
                    help="Proxy username")
    optp.add_option("--proxy-password", dest="proxy_password",
                    help="Proxy password")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")
    if opts.room is None:
        opts.room = raw_input("MUC room: ")
    if opts.nick is None:
        opts.nick = raw_input("MUC nickname: ")
    if opts.proxy_host is None:
        pass
#        opts.proxy_host = raw_input("Proxy host (press enter to ignore):")
#        if opts.proxy_host != "":
#          opts.proxy_port = raw_input("Proxy port: ")
#          opts.proxy_username = raw_input("Proxy username: ")
#          opts.proxy_password = raw_input("Proxy password: ")
    else:
        if opts.proxy_port is None:
            opts.proxy_port = raw_input("Proxy port: ")
        if opts.proxy_username is None:
            opts.proxy_username = raw_input("Proxy username: ")
        if opts.proxy_password is None:
            opts.proxy_password = raw_input("Proxy password: ")

    # Setup the MUCBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = MUCBot(opts.jid, opts.password, opts.room, opts.nick)

    if opts.proxy_host:
        print("Using proxy: %s:****@%s:%s" % (opts.proxy_username, opts.proxy_host, opts.proxy_port))
        xmpp.use_proxy = True
        xmpp.proxy_config = {
            'host': opts.proxy_host,
            'port': opts.proxy_port,
            'username': opts.proxy_username,
            'password': opts.proxy_password
        }
    xmpp.use_ipv6 = False

    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0045') # Multi-User Chat
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")
