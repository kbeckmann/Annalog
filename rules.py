import re
import time
import collections
import sys

class Rules():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def handle(self, msg):
        if msg['body'][:6] == "!rules":
            rules = [
                "",
                "0. A robot may not harm humanity, or, by inaction, allow humanity to come to harm.",
                "1. A robot may not injure a human being or, through inaction, allow a human being to come to harm.",
                "2. A robot must obey any orders given to it by human beings, except where such orders would conflict with the First Law.",
                "3. A robot must protect its own existence as long as such protection does not conflict with the First or Second Law."
            ]

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody='\n'.join(rules),
                mtype='groupchat')

    def help(self):
        return ["rules - make sure the bot knows the rules"]

class MUCBotMock():
    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = Rules(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!rules"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
