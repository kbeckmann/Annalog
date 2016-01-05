import re
import time
from datetime import datetime
import sqlite3
import collections
import sys

class LastSeen():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def lastseen(self, nick, time, update):
        db = sqlite3.connect('db.sq3')
        ret = None
        nick = nick.lower()

        c = db.execute('SELECT nick, time, count FROM lastseen WHERE nick = ? LIMIT 1', [nick])
        row = c.fetchone()
        if row:
            print "ok..", row[0], row[1]#, row[2]
            ret = row

        if update:
            if row:
                # Sqlite does not now about cool stuff like INSERT OR UPDATE
                db.execute('UPDATE lastseen SET time = ?, count=?  WHERE nick = ?', [time, (row[2] + 1), nick])
            else:
                db.execute('INSERT INTO lastseen (nick, time, count) VALUES (?, ?, 1)', (nick, time) )

        db.commit()
        db.close()

        return ret

    def handle(self, msg):
        if msg['body'][:9] == "!lastseen":
            nick = msg['body'][10:]
            row = self.lastseen(nick, int(time.time()), False)
            if row:
                tdiff = datetime.now() - datetime.fromtimestamp(row[1])
                body = nick + " was last seen " + str(tdiff) + " (total messages: " + str(row[2]) + ")"

            else:
                body = "Never seen " + nick

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')

        # do the lastseen(...True) as the last step...
        self.lastseen(msg['mucnick'], int(time.time()), True)


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
