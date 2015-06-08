import binascii

class SigningAlgo():
	def __init__(self, private_key, public_key):
		raise NotImplementedError("Implement __init__()")
	def sign(self, message):
		raise NotImplementedError("Implement sign()")
	def export_private_key(self):
		raise NotImplementedError("Implement export_private_key()")
	def export_public_key(self):
		raise NotImplementedError("Implement export_public_key()")
	def compare_to(self, other):
		if isinstance(other, SigningAlgo) and \
			self.export_private_key() == other.export_private_key() and \
			self.export_public_key() == other.export_public_key():
			return True
		return False
	@classmethod
	def verify(klass, key, signature, message):
		raise NotImplementedError("Implement verify()")
		

# Elliptic curve based signing. 'pip install ecdsa'. todo: change to ed25519
from ecdsa import SigningKey, VerifyingKey, SECP256k1
class ECDSASigner(SigningAlgo):
	def __init__(self, private_key, public_key):
		if not private_key:
			self.private_key = SigningKey.generate(curve=SECP256k1)
			public_key = None
		else:
			self.private_key = SigningKey.from_der(private_key)
		if not public_key:
			self.public_key = self.private_key.get_verifying_key()
		else:
			self.public_key = VerifyingKey.from_der(public_key)
	def sign(self, message):
		return self.private_key.sign_deterministic(message)
	def export_private_key(self):
		return self.private_key.to_der()
	def export_public_key(self):
		return self.public_key.to_der()
	@classmethod
	def verify(klass, key, signature, message):
		key = VerifyingKey.from_der(key)
		return key.verify(signature, message)

# ED25519 using NaCl. 'pip install pynacl'
import nacl.encoding
import nacl.signing
class ED25519Signer(SigningAlgo):
	def __init__(self, private_key, public_key):
		if not private_key:
			self.private_key = nacl.signing.SigningKey.generate()
			public_key = None
		else:
			self.private_key = nacl.signing.SigningKey(private_key)
		if not public_key:
			self.public_key = self.private_key.verify_key
		else:
			self.public_key = nacl.signing.VerifyKey(public_key)
	def sign(self, message):
		return self.private_key.sign(message).signature
	def export_private_key(self):
		return self.private_key.encode()
	def export_public_key(self):
		return self.public_key.encode()
	@classmethod
	def verify(klass, key, signature, message):
		key = nacl.signing.VerifyKey(key)
		return key.verify(signature + message)



# Classic DSA siging 'pip install pycrypto'
from Crypto.Random import random
from Crypto.PublicKey import DSA
from Crypto.Hash import SHA
from Crypto.Util import asn1
import marshal
class DSASigner(SigningAlgo):
	def __init__(self, private_key, public_key):
		if not private_key:
			self.private_key = DSA.generate(1024)
			public_key = None
		else:
			self.private_key = DSASigner.import_der(private_key)
		if not public_key:
			self.public_key = self.private_key.publickey()
		else:
			self.public_key = DSASigner.import_der(public_key)


	def sign(self, message):
		h = self.hash_for_signature(message)
		k = random.StrongRandom().randint(1, self.private_key.q - 1)
		sign = self.private_key.sign(h, k)
		s = marshal.dumps(sign)
		return s
	def export_private_key(self):
		return DSASigner.export_key(self.private_key)
	def export_public_key(self):
		return DSASigner.export_key(self.public_key)
	@classmethod
	def hash_for_signature(klass, message):
		return SHA.new(message).digest()
	@classmethod
	def verify(klass, key, signature, message):
		key = klass.import_der(key)
		s = marshal.loads(signature)
		return key.verify(klass.hash_for_signature(message), s)
		
	@classmethod
	def import_der(self, der):
		seq = asn1.DerSequence()
		seq.decode(der)
		p, q, g, y, x = seq[1:]
		return DSA.construct((y, g, p, q, x))
	@classmethod
	def export_key(klass, key):
		seq = asn1.DerSequence()
		x = key.x if hasattr(key, 'x') else 0
		seq[:] = [0, key.p, key.q, key.g, key.y, x]
		seq = seq.encode()
		return seq

import unittest

class SigningAlgoTester(object):
	def set_signing_algo(self, signing_algo):
		self.signing_algo = signing_algo
	def generate(self):
		T1 = self.signing_algo(None, None)
		private_key = T1.private_key
		public_key = T1.public_key
		self.assertIsNotNone(public_key)
		self.assertIsNotNone(private_key)

		T2 = self.signing_algo(T1.export_private_key(), None)
		self.assertTrue(T1.compare_to(T2))
		self.assertTrue(T2.compare_to(T1))

		T3 = self.signing_algo(T1.export_private_key(), T1.export_public_key())
		self.assertTrue(T1.compare_to(T3))
		self.assertTrue(T3.compare_to(T1))

		T4 = self.signing_algo(None, T1.export_public_key())
		self.assertFalse(T1.compare_to(T4))
		self.assertFalse(T4.compare_to(T1))

	def sign(self):
		T = self.signing_algo(None, None)
		m = "Hello, world!"
		s = T.sign(m)
		k = T.export_public_key()
		self.assertTrue(self.signing_algo.verify(k, s, m))

class ECDSASignerTest(unittest.TestCase, SigningAlgoTester):
	def test_generate(self):
		self.set_signing_algo(ECDSASigner)
		self.generate()

	def test_sign(self):
		self.set_signing_algo(ECDSASigner)
		self.sign()

class ED25519SignerTest(unittest.TestCase, SigningAlgoTester):
	def test_generate(self):
		self.set_signing_algo(ED25519Signer)
		self.generate()

	def test_sign(self):
		self.set_signing_algo(ED25519Signer)
		self.sign()
		
class DSASignerTest(unittest.TestCase, SigningAlgoTester):
	def test_generate(self):
		self.set_signing_algo(DSASigner)
		self.generate()

	def test_sign(self):
		self.set_signing_algo(DSASigner)
		self.sign()


if __name__ == '__main__':
	unittest.main()

