import re
import time
import json
import urllib
import urllib2
import HTMLParser
import wikipedia
import collections
import sys

class Wiki():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def handle(self, msg):
        if msg['body'][:5] == "!wiki":
            q = msg['body'][6:]

            try:
               page  = wikipedia.page(q)
            except wikipedia.DisambiguationError as dis:
                body = "Got a disambiguation page, maybe try:\n" + '\n'.join(dis.options[:10])
            else:
                summary = page.summary
                while len(summary) > 460:
                    pos = summary.rfind('.')
                    summary = summary[:pos]

                body = "%s\n%s." % (page.url, summary)

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')

    def help(self):
        return ["wiki - return first paragraph from Wikipedia (might be slower for big articles)"]

class MUCBotMock():
    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = Wiki(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!wiki google"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
