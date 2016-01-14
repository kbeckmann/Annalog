import re
import time
import random
import collections
import sys
import parsedatetime.parsedatetime as pdt
from sleekxmpp.xmlstream import scheduler
from datetime import datetime,timedelta
from pytz import timezone
from dateutil import tz
import sqlite3

class Karma():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def handle(self, msg):
        if msg['body'][:6] == "!karma":
            db = sqlite3.connect('db.sq3')
            res = db.execute('SELECT name, karma FROM karma ORDER BY karma DESC LIMIT 20')
            karma = []
            ret = ""
            i = 1
            while True:
                row = res.fetchone()
                if (row):
                    karma.append('{0:3}: {1:24} {2:>7}'.format(i, row[0][:1] +  u'\u2063' + row[0][1:], row[1]))
                    i = i + 1
                else:
                    break

            db.commit()
            db.close()

            if len(karma) > 0:
                self.mucbot.send_message(mto=msg['from'].bare,
                    mbody=u'\u22C6' * 3 + ' Karma:\n' + '\n'.join(karma),
                    mtype='groupchat')
            else:
                self.mucbot.send_message(mto=msg['from'].bare,
                    mbody='No karma yet, check !help for usage',
                    mtype='groupchat')

        elif msg['body'][:3] == '!++' or msg['body'][:3] == '!--':
            name = msg['body'][4:]
            if len(name) == 0:
                self.mucbot.send_message(mto=msg['from'].bare,
                    mbody='Nonononono',
                    mtype='groupchat')

            value = 1 if msg['body'][:3] == '!++' else -1

            db = sqlite3.connect('db.sq3')
            ret = None

            c = db.execute('SELECT karma FROM karma where name = ?', [name])
            row = c.fetchone()
            if row:
                # Sqlite does not now about cool stuff like INSERT OR UPDATE
                db.execute('UPDATE karma SET karma = karma + ? WHERE name = ?', [value, name])
            else:
                db.execute('INSERT INTO karma (name, karma) values (?, ?)', [name, value])

            db.commit()
            db.close()

            if row:
                value = value + row[0]

            body = u'\u22C6' * 3 + ' New karma value for %s: %d' % (name, value)
            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')

    def help(self):
        return ['karma - show karma rating. !++ <name> or !-- <name> to add or take away karma']

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
    x = Karma(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!++ mate"}
    x.handle(msg)

    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!++ mate"}
    x.handle(msg)

    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!-- chips"}
    x.handle(msg)

    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!karma"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
