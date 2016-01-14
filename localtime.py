import re
import time
import sys
from datetime import datetime,timedelta
from dateutil import tz

class LocalTime():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def handle(self, msg):
        if msg['body'][:5] == "!time":
            localTime = datetime.now(tz.tzlocal())
            body = "Local time: %s" % localTime.strftime('%Y-%m-%d %H:%M:%S')

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')

    def help(self):
        return ['time - show local time']

class SchedulerMock():
    def add(self, name, seconds, callback, repeat=False):
        return

class MUCBotMock():
    def __init__(self):
        self.scheduler = SchedulerMock()

    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = LocalTime(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!time"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
