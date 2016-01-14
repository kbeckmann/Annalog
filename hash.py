import re
import time
import hashlib
import binascii
import base64
import collections
import string
import sys

class Hash():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def handle(self, msg):
        body = ""
        if msg['body'][:4] == "!md5":
            param = msg['body'][5:]
            body = "md5(\"%s\") = %s" % (param, hashlib.md5(param).hexdigest())
        elif msg['body'][:5] == "!sha1":
            param = msg['body'][6:]
            body = "sha1(\"%s\") = %s" % (param, hashlib.sha1(param).hexdigest())
        elif msg['body'][:7] == "!sha256":
            param = msg['body'][8:]
            body = "sha256(\"%s\") = %s" % (param, hashlib.sha256(param).hexdigest())
        elif msg['body'][:7] == "!sha512":
            param = msg['body'][8:]
            body = "sha512(\"%s\") = %s" % (param, hashlib.sha512(param).hexdigest())
        elif msg['body'][:6] == "!crc32":
            param = msg['body'][7:]
            body = "crc32(\"%s\") = %08x" % (param, binascii.crc32(param) & 0xffffffff)
        elif msg['body'][:7] == "!base64":
            param = msg['body'][8:]
            body = "base64(\"%s\") = %s" % (param, base64.b64encode(param))
        elif msg['body'][:9] == "!unbase64":
            param = msg['body'][10:]
            try:
                decoded = base64.b64decode(param)
            except:
                body = "That's not valid base64!"
            else:
                if all(c in string.printable for c in decoded):
                    body = "unbase64(\"%s\") = %s" % (param, decoded)
                else:
                    body = "unbase64(\"%s\") = binary: %s" % (param, decoded.encode('hex'))

        if len(body) > 0:
            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')

    def help(self):
        ret = []
        ret.append("md5, sha1, sha256, sha512, crc32, base64, unbase64 - return misc hash/checksum")
        return ret

class MUCBotMock():
    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = Hash(MUCBotMock())
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!md5 aaa"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!sha1 aaa"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!sha aaa"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!sha256 aaa"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!sha512 aaa"}
    x.handle(msg)
    
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!crc32 aaa"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
