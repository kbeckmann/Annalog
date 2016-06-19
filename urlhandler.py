import re
import json
import time
import hashlib
import sqlite3
import collections
import sys
from datetime import datetime

class URLHandler():
    def __init__(self, mucbot):
        self.mucbot = mucbot
        self.salt1 = "happy happy hippo"
        self.salt2 = "sad pandas are sad"
        self.whitelist = ["1b49f24e1acf03ef8ad1b803593227ca1b94868c29d41a8ab22fbc7b6d94342c"]
        self.url_history = collections.deque(maxlen=1000)

    def hash(self, plaintext):
        return hashlib.sha256(self.salt1 + str(plaintext) + self.salt2).hexdigest()

    def get_or_set(self, url_plaintext, nick, time):
        url = self.hash(url_plaintext)
        db = sqlite3.connect('db.sq3')
        ret = None

        if url in self.whitelist:
            return None

        c = db.execute('SELECT * FROM urls WHERE url = ? ORDER BY time DESC LIMIT 1', [url])
        row = c.fetchone()
        if row:
             ret = row
             # Sqlite does not now about cool stuff like INSERT OR UPDATE
             db.execute('UPDATE urls SET count=count+1 WHERE url = ?', [url])
        else:
             db.execute('INSERT INTO urls (nick, url, time) VALUES (?,?,?)', (nick, url, time) )

        db.commit()
        db.close()

        return ret

    def entry_to_string(self, entry):
        nick = entry['nick'][0] + u'\u2063' + entry['nick'][1:]
        return nick + ": " + entry['url']

    def handle(self, msg):
        if msg['body'][:4] == "!url":
            matches = []
            if len(msg['body']) > 5 and msg['body'][4] == ' ':
                for entry in self.url_history:
                    if msg['body'][5:] in entry['url']:
                        matches.append(entry)

                if len(matches) > 0:
                    self.mucbot.send_message(mto=msg['from'].bare,
                        mbody="URL History (matching \"%s\"):\n%s" % (msg['body'][5:], "\n".join([self.entry_to_string(x) for x in matches])),
                        mtype='groupchat')
                else:
                    self.mucbot.send_message(mto=msg['from'].bare,
                        mbody="URL History: Nothing found for \"%s\"" % msg['body'][5:],
                        mtype='groupchat')
            else:
                q_size = len(self.url_history)
                self.mucbot.send_message(mto=msg['from'].bare,
                    mbody="URL History: %s" % ("Empty" if q_size == 0 else "\n" + "\n".join([self.entry_to_string(self.url_history[i]) for i in range(max(0, q_size-10), q_size)])),
                    mtype='groupchat')

        if msg['body'][:11] == "URL History" or msg['body'][:1] == "!" or msg['mucnick'] == "Annarchy" or msg['mucnick'] == "Annartur":
            return

        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', msg['body'])
        if not urls:
            return

        for url in urls:
            if url not in self.url_history:
                self.url_history.append({"url": url, "nick" : msg['mucnick']})

            urldata = self.get_or_set(url, msg['mucnick'], int(time.time()))
            karma = 0

            if urldata:
                if urldata[0].lower() == msg['mucnick'].lower():
                    pass
                else:
                    karma = -1

                    tdiff = datetime.now() - datetime.fromtimestamp(urldata[2])
                    self.mucbot.send_message(mto=msg['from'].bare,
                        mbody="%s: Oooooooooold! %s was first (%s)" % (msg['mucnick'], urldata[0], tdiff),
                        mtype='groupchat')
            else:
                karma = 1

            name = msg['mucnick']
            db = sqlite3.connect('db.sq3')
            c = db.execute('SELECT karma FROM karma where lower(name) = lower(?)', [name])
            row = c.fetchone()
            if row:
                db.execute('UPDATE karma SET karma = karma + ? WHERE lower(name) = lower(?)', [karma, name])
            else:
                db.execute('INSERT INTO karma (name, karma) values (lower(?), ?)', [name, karma])

            db.commit()
            db.close()


    def help(self):
	return []

# Importer
def do_import(path):
    db = sqlite3.connect('db.sq3')
    with open(path) as f:
        urls = [json.loads(line) for line in f]
        for url in urls:
            db.execute('INSERT INTO urls (nick, url, time) VALUES (?,?,?)', (url['nick'], url['url'], url['timestamp']) )

    db.commit()
    db.close()

# Test and mock
class MUCBotMock():
    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = URLHandler(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "hello http://events.ccc.de/congress/22014"}
    x.handle(msg)

    print "searching for blabla.."
    x.handle({"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!url blabla"})

    print "searching for ccc"
    x.handle({"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!url ccc"})

    for i in range(20):
        x.handle({"from" : FromMock("channel@example.com"), "mucnick" : "foobar", "body" : "look here http://example.com/" + str(i)})

    x.handle({"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!url example"})

    x.handle({"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!url"})


if __name__ == "__main__":
    if len(sys.argv) == 2:
        do_import(sys.argv[1])
    else:
        do_test()
