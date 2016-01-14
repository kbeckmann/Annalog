import re
import time
import sys
from datetime import datetime,timedelta
from dateutil import tz

class UpTime():
    def __init__(self, mucbot):
        self.mucbot = mucbot
        self.startTime = datetime.now()

    def delta_string(self, delta):
        h = divmod(delta.seconds, 3600)
        m = divmod(h[1], 60)
        s = divmod(m[1], 60)

        t = []
        if delta.days > 0:
            t.append("%d day%s" % (delta.days, "" if delta.days == 1 else "s"))

        if h[0] > 0:
            t.append("%d hour%s" % (h[0], "" if h[0] == 1 else "s"))

        if m[0] > 0:
            t.append("%d minute%s" % (m[0], "" if m[0] == 1 else "s"))

        if s[1] > 0:
            t.append("%d second%s" % (s[1], "" if s[0] == 1 else "s"))

        if len(t) == 0:
            t.append('ett ' + u'\u00F6' + 'gonblick')

        return ' '.join(t)

    def handle(self, msg):
        if msg['body'][:7] == "!uptime":
            nowTime = datetime.now()
            bot = nowTime - self.startTime

            with open('/proc/uptime', 'r') as f:
                upSeconds = float(f.readline().split()[0])
                server = timedelta(seconds = upSeconds)

            body = 'Uptime: bot - %s, server - %s' % (self.delta_string(bot), self.delta_string(server))

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')

    def help(self):
        return ['uptime - show uptime']

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
    x = UpTime(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!uptime"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
