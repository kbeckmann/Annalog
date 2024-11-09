import re
import time
import pafy
import collections
import sys
import requests
import json


class Bluesky():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def handle(self, msg):
        if msg['body'][:11] == "URL History" or msg['body'][:1] == "!" or msg['mucnick'] == "Annarchy":
            return

        skeets = re.findall('(?:https?://|//)?(?:www\.|m\.)?(?:(?:bsky)\.app/profile/([A-z0-9_\-\.]*)/post/([A-z0-9]*))', msg['body'])
        if not skeets:
            return

        for skeet in skeets:
            data = self.get_skeet(skeet[0], skeet[1])
            if not data:
                continue

            body = "Skeet by %s: \"%s\"" % (data[0], data[1])

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')

    def get_skeet(self, handle, post_id):
        response = requests.get('https://public.api.bsky.app/xrpc/com.atproto.identity.resolveHandle', params={'handle': handle})
        if response.status_code == 200:
            user_data = response.json()
            user_did = user_data.get('did')

        if not user_did:
            return None

        post_uri = 'at://{}/app.bsky.feed.post/{}'.format(user_did, post_id)
        response = requests.get('https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread', params={'uri': post_uri})

        if response.status_code != 200:
            return None

        post_data = response.json()
        print(post_data)
        thread = post_data.get('thread')

        if thread and 'post' in thread:
            post = thread['post']
            author = post['author']
            post_text = post.get('record', {}).get('text')

            if post_text:
                return author['displayName'], post_text

    def help(self):
        return []

class MUCBotMock():
    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = Bluesky(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "skeet https://bsky.app/profile/arturo182.bsky.social/post/3lahe7rrkav25"}
    x.handle(msg)

    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "lol https://bsky.app/profile/kicad.org/post/3l63pj24ufb2o lol"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
