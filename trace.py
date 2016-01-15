import subprocess

class Trace():
    def __init__(self, mucbot):
        self.mucbot = mucbot

    def trace(self, host):
        p = subprocess.Popen(['mtr', host, '--report', '-c', '1'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        return out

    def handle(self, msg):
        if msg['body'][:6] == "!trace":
            host = msg['body'][7:]
            body = ''.join(["Tracing ", host, "\n", self.trace(host)])
            print(body)

            self.mucbot.send_message(mto=msg['from'].bare,
                mbody=body,
                mtype='groupchat')

    def help(self):
        return ["mtr - traces a host"]

class MUCBotMock():
    def send_message(self, mto, mbody, mtype):
        print "MUCBotMock:", mto, mbody, mtype

class FromMock():
    def __init__(self, _from):
        self.bare = _from

def do_test():
    x = Trace(MUCBotMock())

    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!trace localhost && pwd && ls"}
    x.handle(msg)

    msg = {"from" : FromMock("channel@example.com"), "mucnick" : "kallsse", "body" : "!trace google.com"}
    x.handle(msg)

if __name__ == "__main__":
    do_test()
