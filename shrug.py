import re
import time
import collections
import sys

class Shrug():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def handle(self, msg):
        if msg['body'][:6] == "!shrug":
            say = ""

            if len(msg['body']) > 6:
              say = "\n      /" + u'\u00AF' + "- %s\n" % msg['body'][7:]

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=say + u'\u00AF' + '\\_' + u'\u0028' + u'\u30C4' + u'\u0029' + '_/' + u'\u00AF',
                mtype='groupchat')

    def help(self):
        return []

class MUCBotMock():
    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = Shrug(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!shrug"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
