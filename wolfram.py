import re
import time
import json
import urllib
import urllib2
import HTMLParser
from xml.etree import ElementTree
import collections
import sys

class Wolfram():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def handle(self, msg):
        if msg['body'][:8] == "!wolfram":
            q = msg['body'][9:].encode('utf-8')

            result = urllib2.urlopen("http://api.wolframalpha.com/v2/query?format=plaintext&input=" + urllib.quote_plus(q) + "&appid=3KEKLK-GVJTEP28YK")
            xml = result.read()
            root = ElementTree.fromstring(xml)
            pods = root.findall('pod')
            dyms = root.findall('didyoumeans')
            res = []
            body = ""

            # we got some results
            for pod in pods[:6]:
                if pod.get('id') != 'Input' and pod.findtext('subpod/plaintext') != '':
                    text = pod.findtext('subpod/plaintext')
                    res.append(pod.get('title') + ': \n' + '\n'.join(["    {0}".format(t.strip()) for t in text.split('\n')]))

            # no results but suggestions
            if len(dyms) > 0:
                res2 = []
                for d in dyms[0].findall("didyoumean"):
                    res2.append(d.text)

                res.append("Did you mean: " + ('\n' if len(res2) > 1 else '') + '\n'.join(res2))

            if len(res) > 0:
                body = ('\n' if len(pods) > 1 else '') + '\n'.join(res)

            # what is happening?!?!
            if len(pods) == 0 and len(dyms) == 0:
                body = "%s: No idea what you meant." % msg['mucnick']

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')

    def help(self):
        return ["wolfram - return WolframAlpha result (might be slow)"]

class MUCBotMock():
    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = Wolfram(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!wolfram 2+2"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
