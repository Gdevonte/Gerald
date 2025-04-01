import Crypto
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import binascii

class Transaction:
    def __init__(self, sender, recipient, amount, signature):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    def to_dict(self):
        return self.__dict__

class Blockchain:
    def verify_transaction_signature(self, sender_public_key, signature, transaction):
        public_key = RSA.importKey(binascii.unhexlify(sender_public_key))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new(str(transaction).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))
