import re
import time
from datetime import datetime
import sqlite3
import collections
import sys

class LastSeen():
    def __init__(self, mucbot):
        self.mucbot = mucbot

        # merge nick_m and nick
        db = sqlite3.connect('db.sq3')
        c = db.execute('SELECT nick, count from lastseen WHERE nick like "%_m"')
        while True:
            row = c.fetchone()
            if (row):
                db.execute('UPDATE lastseen SET count = count + ? WHERE nick = ?', [row[1], row[0][:-2]])
            else:
                break

        db.execute('DELETE FROM lastseen WHERE nick like "%_m"')
        db.commit()
        db.close()

    def lastseen(self, nick, count, time, update):
        if len(nick) > 2 and nick.endswith("_m"):
            nick = nick[:-2]

        db = sqlite3.connect('db.sq3')
        ret = None

        c = db.execute('SELECT nick, time, count FROM lastseen WHERE nick = ? LIMIT 1', [nick])
        row = c.fetchone()
        if row:
            ret = row

        if update:
            if count > 400:
                count = 400
            if row:
                # Sqlite does not now about cool stuff like INSERT OR UPDATE
                db.execute('UPDATE lastseen SET time = ?, count=?  WHERE nick = ?', [time, (row[2] + count), nick])
            else:
                db.execute('INSERT INTO lastseen (nick, time, count) VALUES (?, ?, ?)', (nick, time, count) )

        db.commit()
        db.close()

        return ret

    def stats(self):
        ret = ""
        db = sqlite3.connect('db.sq3')

        c = db.execute('SELECT nick, sum(count), round(sum(count)*100)/(select sum(count) from lastseen) FROM lastseen GROUP BY lower(nick) ORDER BY sum(count) DESC LIMIT 10')
        i = 1
        while True:
            row = c.fetchone()
            if (row):
                ret = ret + '{0:3}: {1:24} {2:>7} {3:5.2f}%\n'.format(i, row[0][:1] +  u'\u2063' + row[0][1:], row[1], row[2])
                i = i + 1
            else:
                break

        db.close()

        return ret[:-1] 

    def handle(self, msg):
        if msg['body'][:9] == "!lastseen":
            nick = msg['body'][10:]
            row = self.lastseen(nick, 0, int(time.time()), False)
            if row:
                tdiff = datetime.now() - datetime.fromtimestamp(row[1])
                h = divmod(tdiff.seconds, 3600)
                m = divmod(h[1], 60)
                s = divmod(m[1], 60)

                t = []
                if tdiff.days > 0:
                    t.append("%d day%s" % (tdiff.days, "" if tdiff.days == 1 else "s"))

                if h[0] > 0:
                    t.append("%d hour%s" % (h[0], "" if h[0] == 1 else "s"))

                if m[0] > 0:
                    t.append("%d minute%s" % (m[0], "" if m[0] == 1 else "s"))

                if s[1] > 0:
                    t.append("%d second%s" % (s[1], "" if s[0] == 1 else "s"))

                if len(t) == 0:
                    body = nick + " is here right now!"
                else:
                    body = nick + " was last seen " + ", ".join(t) + " ago"
            else:
                body = "Never seen " + nick

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')
        elif msg['body'][:6] == "!stats":
            body = 'Stats: \n' + self.stats()
            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')
        if not msg['mucnick'].startswith('Anna'):
            # do the lastseen(...True) as the last step...
            self.lastseen(msg['mucnick'], len(msg['body']), int(time.time()), True)

    def help(self):
        ret = []
        ret.append("lastseen - check when nick was last seen")
        ret.append("stats - see top 10 spammers")
        return ret

class MUCBotMock():
    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = LastSeen(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "hello http://events.ccc.de/congress/22014"}
    x.handle(msg)

    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!lastseen kallsse"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
