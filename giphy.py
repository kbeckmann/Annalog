import re
import time
import json
import urllib
import urllib2
import HTMLParser
import collections
import sys

class Giphy():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def giphy(self, q):
        data = json.load(urllib2.urlopen("http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag=%s" % urllib.quote_plus(q)))

        if len(data["data"]) > 0:
            return data["data"]["image_original_url"];

        return "https://media.giphy.com/media/4SD55a1RnZCdq/giphy.gif"

    def handle(self, msg):
        if msg['body'][:6] == "!giphy":
            q = msg['body'][7:]

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=self.giphy(q),
                mtype='groupchat')

    def help(self):
        return ["giphy - return a random GIF"]

class MUCBotMock():
    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = Giphy(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!giphy ship it"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
