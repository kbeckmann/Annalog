import re
import time
import urllib2
import collections
import sys

class IsUp():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def handle(self, msg):
        body = ""
        if msg['body'][:5] == "!isup":
            url = msg['body'][6:]

            if len(url) == 0:
                body = "Stop screwing around!"
            else:
                resp = urllib2.urlopen("http://isup.me/%s" % url).read()
                if "Huh?" in resp:
                    body = "How about a valid URL next time?"
                else:
                    body = "%s seems to be %s!" % (url, "down" if "looks down" in resp else "up")

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
    x = IsUp(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!isup www.google.com"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!isup http://www.google.com/"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!isup google.com"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!isup unit_testing_is_the_shit.com"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!isup what"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!isup 112123"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
