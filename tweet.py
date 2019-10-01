import re
import time
import pafy
import collections
import sys
import twitter
from t import ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET

class Twitter():
    def __init__(self, mucbot):
        self.mucbot = mucbot
        self.api = twitter.Api(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)

    def handle(self, msg):
        if msg['body'][:11] == "URL History" or msg['body'][:1] == "!" or msg['mucnick'] == "Annarchy":
            return

        statuses = re.findall('(?:https?://|//)?(?:www\.|m\.)?(?:twitter\.com/(?:[A-z0-9_-]*/status/))([\w-]*)(?![\w-])', msg['body'])
        if not statuses:
            return

        for status in statuses:
            data = self.api.GetStatus(status)
            body = "Tweet by %s: \"%s\"" % (data.user.screen_name, data.text)

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
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
    x = Twitter(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "funny tweet https://twitter.com/arturo182/status/1173662286021582848"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "lol https://twitter.com/hacker0x01/status/1177234032452653056?s=21 lol"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
