import re
import time
import pafy
import collections
import sys
import requests
import json
import html2text

class Mastodon():
    def __init__(self, mucbot):
        self.mucbot = mucbot
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = True
        self.h2t.body_width = 0
        self.h2t.ignore_images = True
        self.h2t.ignore_emphasis = True
        self.h2t.ignore_tables = True

    def handle(self, msg):
        if msg['body'][:11] == "URL History" or msg['body'][:1] == "!" or msg['mucnick'] == "Annarchy":
            return

        toots = re.findall('((?:https?://|//)?(?:www\.|m\.)?(?:[\w]*\.[\w]*))/@(?:[A-z0-9_-]*/)([0-9]*)(?![\w-])', msg['body'])
        if not toots:
            return

        for toot in toots:
            data = self.get_toot(toot[0], toot[1])
            if not data:
                continue

            body = "Toot by %s: \"%s\"" % (data[0], data[1])

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')

    def get_toot(self, url, status_id):
        try:
            response = requests.get('%s/api/v1/statuses/%s' % (url, status_id))
        except:
            return None

        if response.status_code == 200:
            data = response.json()
            account = data.get('account')
            content = self.h2t.handle(data.get('content')).strip()
            media = data.get('media_attachments')

        if account and (content or len(media) > 0):
            author = account.get('display_name')
            body = content[:200]

            if len(media) > 0:
              body += ' ' + media[0].get('url') + ' '

            return author, body

    def help(self):
        return []

class MUCBotMock():
    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = Mastodon(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "toot https://digipres.club/@foone/114617608056238671"}
    x.handle(msg)

    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "lol https://hackaday.socxial/@hackaday/114617703674576070 lol"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()

