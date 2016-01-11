import re
import time
import pafy
import collections
import sys

class YouTube():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def handle(self, msg):
        if msg['body'][:11] == "URL History" or msg['body'][:1] == "!" or msg['mucnick'] == "Annarchy":
            return

        urls = re.findall('(?:https?://|//)?(?:www\.|m\.)?(?:youtu\.be/|youtube\.com/(?:embed/|v/|watch\?v=|watch\?.+&v=))([\w-]{11})(?![\w-])', msg['body'])
        if not urls:
            return

        for url in urls:
            video = pafy.new(url)
            body = "Video Title: \"%s\" Duration: %s" % (video.title, video.duration)

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
    x = YouTube(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "check this video! http://www.youtube.com/watch?v=cyMHZVT91Dw"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
