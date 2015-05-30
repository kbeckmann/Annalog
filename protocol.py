import binascii
import hashlib
import hmac
import base64
import json
from Crypto import Random

# Elliptic curve based signing. 'pip install ecdsa'. todo: change to ed25519
from ecdsa import SigningKey, VerifyingKey, SECP256k1

# Elliptic curve based PKI encryption. 'pip install curve25519-donna'
from curve25519 import Private, Public

# AES-CBC wrapper
from aescipher import AESCipher


class TrustedGroupCommunication():
    def __init__(self, private_signing_key_der, public_signing_key_der,
                 private_encryption_key, public_encryption_key,
                 context, user):
        self.trusted_public_signing_keys = {}
        self.trusted_public_signing_keys_users = []

        self.trusted_public_encryption_keys = {}
        self.trusted_public_encryption_keys_users = []
        self.imported_secrets = {}

        self.private_signing_key = SigningKey.from_der(private_signing_key_der)
        self.public_signing_key = VerifyingKey.from_der(public_signing_key_der)
        self.private_encryption_key = Private(secret=private_encryption_key)
        self.public_encryption_key = Public(public=public_encryption_key)

        self.secret = None
        self.context = context
        self.user = user

        self.refresh_secret()


    @classmethod
    def from_key_file(klass, key_file, context, user):
        with open(key_file) as f:
            keys = json.loads(f.read())
            return klass(
                binascii.unhexlify(keys["private_signing_key"]),
                binascii.unhexlify(keys["public_signing_key"]),
                binascii.unhexlify(keys["private_encryption_key"]),
                binascii.unhexlify(keys["public_encryption_key"]),
                context, user)

    @classmethod
    def generate(klass, context, user):
        private_signing_key = SigningKey.generate(curve=SECP256k1)
        public_signing_key = private_signing_key.get_verifying_key()
        private_encryption_key = Private(secret=Random.new().read(32))
        public_encryption_key = private_encryption_key.get_public()
        return klass(private_signing_key.to_der(),
                     public_signing_key.to_der(),
                     private_encryption_key.serialize(),
                     public_encryption_key.serialize(),
                     context, user)


    def load_private_signing_key(self, der):
        if der:
            self.private_signing_key = SigningKey.from_der(der)
        else:
            self.private_signing_key = SigningKey.generate(curve=SECP256k1)
            print "Generated private signing key"
        self.public_signing_key = self.private_signing_key.get_verifying_key()

    def load_private_encryption_key(self, key):
        if key and len(key) == 32:
            self.private_encryption_key = Private(secret=key)
        else:
            print "Generating private encryption key"
            key = Random.new().read(32)
            self.private_encryption_key = Private(secret=key)

        self.public_encryption_key = self.private_encryption_key.get_public()


    def refresh_secret(self):
        self.secret = Random.new().read(32)
        self.imported_secrets[self.user] = self.secret

    ''' Public API '''
    def add_trusted_public_signing_key(self, name, der):
        if name in self.trusted_public_signing_keys_users:
            return False
        self.trusted_public_signing_keys_users.append(name)
        self.trusted_public_signing_keys[name] = VerifyingKey.from_der(der)
        return True

    def add_trusted_public_encryption_key(self, name, key):
        if name in self.trusted_public_encryption_keys_users:
            return False
        self.trusted_public_encryption_keys_users.append(name)
        self.trusted_public_encryption_keys[name] = Public(public=key)
        return True

    def export_private_signing_key(self):
        return self.private_signing_key.to_der()

    def export_public_signing_key(self):
        return self.public_signing_key.to_der()

    def export_private_encryption_key(self):
        return self.private_encryption_key.serialize()

    def export_public_encryption_key(self):
        return self.public_encryption_key.serialize()

    def export_all_keys(self):
        return json.dumps({"private_signing_key" : binascii.hexlify(self.export_private_signing_key()),
                           "public_signing_key"  : binascii.hexlify(self.export_public_signing_key()),
                           "private_encryption_key" : binascii.hexlify(self.export_private_encryption_key()),
                           "public_encryption_key" : binascii.hexlify(self.export_public_encryption_key())});

    def sign(self, msg):
        return self.private_signing_key.sign_deterministic(msg)

    def get_shared_aes_key_from(self, user):
        if user not in self.trusted_public_signing_keys_users:
            return False
        user_pub = self.trusted_public_encryption_keys[user]
        shared_secret = self.private_encryption_key.get_shared_key(user_pub)
        key = hmac.new(self.context, msg=shared_secret, digestmod=hashlib.sha256).digest()
        aes = AESCipher(key)
        return aes

    def export_secret_to(self, user):
        aes = self.get_shared_aes_key_from(user)
        #if user not in self.trusted_public_signing_keys_users:
        #    return False
        #user_pub = self.trusted_public_encryption_keys[user]
        #shared_secret = self.private_encryption_key.get_shared_key(user_pub)
        #key = hmac.new(self.context, msg=shared_secret, digestmod=hashlib.sha256).digest()
        #aes = AESCipher(key)
        ciphertext = aes.encrypt(self.secret)
        #print "Ciphertext length:", len(ciphertext)
        #print "Cipher: ", binascii.hexlify(ciphertext)
        print "[%s] secret: %s" % (self.user, binascii.hexlify(self.secret))
        #print "self.secretlen: ", len(self.secret)
        signature = self.sign(ciphertext)
        message = ciphertext + signature
        #print "cipher len", len(ciphertext)
        #print "signature len", len(signature)
        #print "Complete message:", binascii.hexlify(message)
        return base64.b64encode(message)

    def import_secret_from(self, user, message):
        if user not in self.trusted_public_encryption_keys_users:
            return False
        msg_bin = base64.b64decode(message)
        print "message in:", binascii.hexlify(msg_bin)
        secret = msg_bin[:80]
        signature = msg_bin[80:]
        if self.verify(user, signature, secret):
            print "Verified key from", user
            aes = self.get_shared_aes_key_from(user)
            secret_plaintext = aes.decrypt(secret)
            print "[%s] decrypted secret from %s: %s" % (self.user, user, binascii.hexlify(secret_plaintext))
            self.imported_secrets[user] = secret_plaintext
        else:
            print "Error importing secret from", user

    def import_secret_completed(self):
        key = ""
        for k, v in self.imported_secrets.iteritems():
            key = hmac.new(self.context, msg=(str(key) + k + v), digestmod=hashlib.sha256).digest()
        print "[%s] Session key: %s" % (self.user, binascii.hexlify(key))
        self.aes_session = AESCipher(key)

    def verify(self, user, signature, msg):
        if user in self.trusted_public_signing_keys_users:
            return self.trusted_public_signing_keys[user].verify(signature, msg)

    def encrypt_message(self, plaintext):
        return self.aes_session.encrypt(plaintext)

    def decrypt_message(self, cipher):
        return self.aes_session.decrypt(cipher)


class Test():

    ''' Agree upon a shared public string, such as the name of a chat room '''
    CONTEXT = "The secret chat room"

    def generate_keys(self):
        self.alice = TrustedGroupCommunication.generate(Test.CONTEXT, "alice")
        self.bob = TrustedGroupCommunication.generate(Test.CONTEXT, "bob")
        self.charlie = TrustedGroupCommunication.generate(Test.CONTEXT, "charlie")

        self.save_key_file(self.alice, "alice.key")
        self.save_key_file(self.bob, "bob.key")
        self.save_key_file(self.charlie, "charlie.key")

    def save_key_file(self, gtp, filename):
        with open(filename, "w") as f:
            keys = gtp.export_all_keys()
            f.write(keys)

    ''' Always call this first in a test to ensure a clean start '''
    def load_keys(self):
        self.alice = TrustedGroupCommunication.from_key_file("alice.key", Test.CONTEXT, "alice")
        self.bob = TrustedGroupCommunication.from_key_file("bob.key", Test.CONTEXT, "bob")
        self.charlie = TrustedGroupCommunication.from_key_file("charlie.key", Test.CONTEXT, "charlie")

    def test_signing(self):
        self.load_keys()
        bob_public_der = self.bob.export_public_signing_key()
        self.alice.add_trusted_public_signing_key("bob", bob_public_der)

        bob_message = "Hello, I am bob."
        bob_message_sig = self.bob.sign(bob_message)
        print "Can Alice verify Bob's message?", self.alice.verify("bob", bob_message_sig, bob_message)

    def key_exchange(self):
        self.load_keys()

        ''' Let all users exchange their public keys '''
        self.alice.add_trusted_public_signing_key("bob", self.bob.export_public_signing_key())
        self.alice.add_trusted_public_encryption_key("bob", self.bob.export_public_encryption_key())

        self.alice.add_trusted_public_signing_key("charlie", self.charlie.export_public_signing_key())
        self.alice.add_trusted_public_encryption_key("charlie", self.charlie.export_public_encryption_key())

        self.bob.add_trusted_public_signing_key("alice", self.alice.export_public_signing_key())
        self.bob.add_trusted_public_encryption_key("alice", self.alice.export_public_encryption_key())

        self.bob.add_trusted_public_signing_key("charlie", self.charlie.export_public_signing_key())
        self.bob.add_trusted_public_encryption_key("charlie", self.charlie.export_public_encryption_key())

        self.charlie.add_trusted_public_signing_key("alice", self.alice.export_public_signing_key())
        self.charlie.add_trusted_public_encryption_key("alice", self.alice.export_public_encryption_key())

        self.charlie.add_trusted_public_signing_key("bob", self.bob.export_public_signing_key())
        self.charlie.add_trusted_public_encryption_key("bob", self.bob.export_public_encryption_key())

    def secret_exchange(self):
        self.key_exchange()

        ''' Let all users exchange their session secrets '''
        self.alice.import_secret_from("bob", self.bob.export_secret_to("alice"))
        self.alice.import_secret_from("charlie", self.charlie.export_secret_to("alice"))
        self.bob.import_secret_from("alice", self.alice.export_secret_to("bob"))
        self.bob.import_secret_from("charlie", self.charlie.export_secret_to("bob"))
        self.charlie.import_secret_from("alice", self.alice.export_secret_to("charlie"))
        self.charlie.import_secret_from("bob", self.bob.export_secret_to("charlie"))

        self.alice.import_secret_completed()
        self.bob.import_secret_completed()
        self.charlie.import_secret_completed()

    def test_chat(self):
        self.secret_exchange()

        alice_msg = "Hello, I'm Alice!"
        print "Alice writes [%s]" % alice_msg
        alice_enc = self.alice.encrypt_message(alice_msg)
        bob_decrypted = self.bob.decrypt_message(alice_enc)
        assert alice_msg == bob_decrypted
        print "Bob decrypted [%s]" % bob_decrypted

    def run(self):
        self.generate_keys()
        self.test_signing()
        self.key_exchange()
        self.secret_exchange()
        self.test_chat()


if __name__ == '__main__':
    Test().run()
    quit()
