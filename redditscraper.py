import praw
import time
from threading import Timer

import re
import json
import time
import hashlib
import sqlite3
import collections
import sys
from datetime import datetime

class RedditScraper():
    def __init__(self, mucbot):
        self.mucbot = mucbot
        self.reddit = praw.Reddit(user_agent='my_cool_application')
        self.history = collections.deque(maxlen=1000)
        self.history_text = collections.deque(maxlen=10)
        self.subreddits = ['programming', 'linux', 'netsec']

    def start(self):
        self.scrape()

    def restart_timer(self):
        Timer(60*1, RedditScraper.scrape, [self]).start()

    def process_subreddit(self, subreddit):
        s = self.reddit.get_subreddit(subreddit).get_hot(limit=25)
        urls = []
        for x in s:
            key = x.short_link
            if not key in self.history:
                self.history.append(key)
                formatted = ("[ %s ] %s" % (x.short_link, str(x)))
                urls.append(formatted)
                self.history_text.append(formatted)
                print formatted
        return urls

    def scrape(self):
        print "ohai!", time.time()
        urls = []
        for subreddit in self.subreddits:
            urls.extend(self.process_subreddit(subreddit))
#        print urls
        msg = "\n".join(urls)
        self.mucbot.send_message(mto=self.mucbot.room,
                                     mbody=msg,
                                     mtype='groupchat')
        self.restart_timer()

    def muc_message(self, msg):
        if msg['body'][:5] == "!last":
            body = "\n".join(self.history_text)
            self.mucbot.send_message(mto=self.mucbot.room,
                                     mbody=body,
                                     mtype='groupchat')
        elif msg['body'][:5] == "!help":
            body = "Commands:\n\t!last\tPrints the last 10 urls"
            self.mucbot.send_message(mto=self.mucbot.room,
                                     mbody=body,
                                     mtype='groupchat')


if __name__ == "__main__":
    R = RedditScraper(None)
    R.start()
