import re
import time
from random import randint
import collections
import sys

class Dice():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def roll(self, i, d):
        sum = 0
        for x in range(0, i):
            sum = sum + randint(1, d)

        return sum

    def handle(self, msg):
        if msg['body'][:5] == "!roll":
            match = re.search("([0-9]?)d([0-9]+)", msg['body'][6:])
            
            if match:
                try:
                   i = int(match.group(1) if match.group(1) is not None else 1)
                except:
                    i = 1
                    
                try:
                    d = int(match.group(2))
                except:
                    d = 6
                    
                body = "Rolled %dd%d: %d" % (i, d, self.roll(i, d))
            else:
                body = "This is serious business, %s..." % msg['mucnick']

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')

class MUCBotMock():
    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = Dice(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!roll d6"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!roll 3d2"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!roll ad10"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!roll asda"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!roll 12312"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
