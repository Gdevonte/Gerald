import binascii
from Crypto.PublicKey import RSA

class Wallet:
    def create_wallet(self):
        private_key = RSA.generate(2048)
        public_key = private_key.publickey()
        return {
            'private_key': binascii.hexlify(private_key.export_key()).decode('ascii'),
            'public_key': binascii.hexlify(public_key.export_key()).decode('ascii')
        }

    def display_balance(self, public_key):
        # Query the blockchain to get the balance for the given public key
        balance = self.query_balance(public_key)
        print(f"Balance for {public_key}: {balance} XKW")
