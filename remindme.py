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

class RemindMe():
    def __init__(self, mucbot):
        self.mucbot = mucbot

        self.mucbot.scheduler.add("check_reminders", 1, self.check_reminders, repeat=True)

    def check_reminders(self):
        nowUtc = time.gmtime()
        nowDb = int(time.mktime(nowUtc))

        db = sqlite3.connect('db.sq3')
        res = db.execute('SELECT sender, nick, msg FROM reminders WHERE time = ?', [nowDb])
        while True:
            row = res.fetchone()
            if (row):
                if row[2] == '':
                    body = "%s: This is a reminder!" % row[1]
                else:
                    body = "%s: Remember to %s!" % (row[1], row[2])

                self.mucbot.send_message(mto=row[0],
                    mbody=body,
                    mtype='groupchat')

            else:
                break

        db.execute('DELETE FROM reminders WHERE time <= ?', [nowDb]);
        db.commit();
        db.close()

    def handle(self, msg):
        if msg['body'][:7] == "!remind":
            req = msg['body'][8:]
            req = req.split("\n")[0]

            # get user
            reqUser = req.split(" ")[0]
            req = req[len(reqUser)+1:]

            if reqUser.lower() == 'me':
                reqUser = msg['mucnick']

            # get message
            reqMsg = ""
            idx = 0
            msgSearch = re.search('(["].{0,9999}["])', req)
            if msgSearch:
               reqMsg = msgSearch.group()[1:-1]
               idx = msgSearch.start(0)

            # get time
	    reqTime = req
            if idx > 0:
                reqTime = req[:idx-1]

            if reqUser == '' or reqTime == '':
                body = "Need user and time, see !help for usage"
            else:
                body = ""
                # convert human time to python time
                try:
                    cal = pdt.Calendar()
                    if cal.parse(reqTime)[1] == 0:
                        body = "For being a dick, the reminder was set for 15 minutes!"
                        reqMsg = "not be a dick anymore"
                        reqUser = msg['mucnick']
                        holdTime = cal.parse("15 minutes", datetime.now(tz.tzlocal()))
                    else:
                        holdTime = cal.parse(reqTime, datetime.now(tz.tzlocal()))
                except:
                    body = "Time out of range"
                else:
                    # local to utc (for db)
                    localTime = datetime.fromtimestamp(int(time.mktime(holdTime[0])))
                    localTime = localTime.replace(tzinfo = tz.tzlocal())
                    nowTime = datetime.now(tz.tzlocal())

                    if localTime > nowTime:
                        utcTime = localTime.astimezone(tz.tzutc())
                        dbTime = int(time.mktime(utcTime.timetuple()))
                        db = sqlite3.connect('db.sq3')
                        db.execute('INSERT INTO reminders (sender, nick, time, msg) VALUES (?, ?, ?, ?)', (msg['from'].bare, reqUser, dbTime, reqMsg) )
                        db.commit()
                        db.close()

                        if body == "":
                            body = "Ok, reminder set for %s :D" % localTime.strftime('%Y-%m-%d %H:%M:%S')
                    elif localTime == nowTime:
                        body = "You can probably remember that long, %s..." % msg['mucnick']
                    else:
                        body = "Stop living in the past, %s!" % msg['mucnick']

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')

    def help(self):
        ret = ""
        ret = ret + "remind - add a reminder, format: '!remind <user> <time> \"[message]\"'\n"
        ret = ret + "        user - nick or 'me'\n"
        ret = ret + "        time - human-readable time, for example '10 minutes', '1 hour 30 minutes'\n"
        ret = ret + "        message (optional) - what to say when the time comes"
        return [ret]

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
    x = RemindMe(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!remind me 1 hour"}
    x.handle(msg)

    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!remind frazz 10 seconds \"do a thing\""}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
