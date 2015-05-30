import re
import json
import time
import hashlib
import sqlite3
import collections
import sys
import binascii
from datetime import datetime
from aescipher import AESCipher

class AESChat():
    def __init__(self, mucbot):
        self.mucbot = mucbot
        self.key = binascii.unhexlify("4293209e7a4638be35c2c291533a3c0be4867b6bd766980458c02b3b029e7df6")
        self.aescipher = AESCipher(self.key)

    def handle(self, msg):
        if msg['body'][:4] == "!MSG":
            cipher = msg['body'][4:]
            plaintext = None
            try:
                if len(cipher) > 16:
                    plaintext = self.aescipher.decrypt(cipher)
            except None:
                pass
            plaintext = "(malformed message)" if not plaintext else plaintext
            self.mucbot.push_message("[%s]: %s" % (msg['mucnick'], plaintext))
        else:
            self.mucbot.push_message("[%s](unenctypted): %s" % (msg['mucnick'], msg['body']))

    def send(self, msg):
        cipher = self.aescipher.encrypt(msg)
        body = "!MSG%s" % cipher
        body = msg
        self.mucbot.send_message(mto=self.mucbot.room,
                          mbody=body,
                          mtype='groupchat')


# Test and mock
class MUCBotMock():
    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = AESChat(MUCBotMock())

    key = binascii.unhexlify("4293209e7a4638be35c2c291533a3c0be4867b6bd766980458c02b3b029e7df6")
    c = AESCipher(key)
    enc = c.encrypt("Hello world!")
    body = "!MSG" + enc
    print "Sending:", body

    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : body}
    x.handle(msg)

    body = "!MSG" + "QUFBQUFBQUFBQUJCQkJCQjEyMzQ1Njc4OTAxMjM0NTYxMjM0NTY3ODkwMTIzNDU2"
    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : body}
    x.handle(msg)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        do_import(sys.argv[1])
    else:
        do_test()
