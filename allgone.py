import re
import urllib
import collections
import sys

class AllGone():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def format_size(self, num, suffix='B'):
        num = int(num)

        for unit in ['','K','M','G','T','P','E','Z']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)

            num /= 1024.0

        return "%.1f%s%s" % (num, 'Yi', suffix)

    def handle(self, msg):
        if msg['mucnick'].startswith("Anna"):
            return

        urls = re.findall('http[s]?://allg.one/[A-z0-9_-]+', msg['body'])
        if not urls:
            return

        for url in urls:
            res = urllib.urlopen(url)
            http = res.info()
            length = http.getheaders('Content-Length')
            if len(length) < 1:
                continue

            body = "%s - %s, %s" % (url, http.type, self.format_size(length[0]))

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')

    def help(self):
        return []

class MUCBotMock():
    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = AllGone(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "check this link, yo: https://allg.one/dBo derp"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
