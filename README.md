# Blockchain 


import json
import requests
import re 
# Added for regex validation
from _sha256 import sha256
from time import time
from typing import Optional
from urllib.parse import urlparse
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
import base64
import secrets  # For private key generation
from web3 import Web3

# Constants for block types
BLOCK_TYPE_COMMON = 'common'
BLOCK_TYPE_STANDARD = 'standard'
BLOCK_TYPE_VIP = 'VIP'
FORGE_TRIGGER = 1

class Blockchain:
    def __init__(self):
        self.authority = None
        self.blocs = []
        self.peers = set()
        self.mempool = {BLOCK_TYPE_COMMON: [], BLOCK_TYPE_STANDARD: [], BLOCK_TYPE_VIP: []}  # Separate pools for different block types
        self.forge(prev_hash='genesis', curr_hash=None)
    
    def generate_private_key(self):
        """Generate a random private key."""
        private_key = secrets.token_hex(32)  # 64-character hex
        return private_key

    def generate_voucher(self, private_key, amount):
        """Wrapper to create vouchers using CryptoVoucher."""
        crypto_voucher = CryptoVoucher()
        voucher_key, voucher_code, error = crypto_voucher.create_voucher(private_key)
        if error:
            return None, error
        return voucher_key, voucher_code

    def validate_voucher(self, voucher_key, voucher_code):
        """Validate a voucher using CryptoVoucher methods."""
        crypto_voucher = CryptoVoucher()
        restored_private_key, error = crypto_voucher.restore_private_key(voucher_key, voucher_code)
        if error:
            return False, error
        return True, restored_private_key

    def redeem_voucher(self, private_key, voucher_key, voucher_code):
        """Redeem a voucher if valid."""
        is_valid, _ = self.validate_voucher(voucher_key, voucher_code)
        if not is_valid:
            return "Voucher is invalid!"
        
        # Add the voucher redemption as a new transaction
        content = {
            "voucher_key": voucher_key,
            "voucher_code": voucher_code,
            "amount": "redeemed"  # Simplified redemption action
        }
        self.new_transaction(sender=private_key, content=content, block_type=BLOCK_TYPE_STANDARD)

        return "Voucher redeemed successfully!"

    def forge(self, prev_hash: Optional[str], curr_hash: Optional[str], block_type: str = BLOCK_TYPE_COMMON):
        """Forge a new block in the blockchain."""
        bloc = {
            'previous_hash': prev_hash or self.previous_block['current_hash'],
            'current_hash': '',
            'timestamp': int(time()),
            'block_type': block_type,
            'transactions': self.mempool[block_type][:]  # Use transactions from the respective mempool
        }

        bloc['current_hash'] = curr_hash or self.hash(bloc)
        self.blocs.append(bloc)
        self.mempool[block_type].clear()  # Clear the mempool after forging the block

    def new_transaction(self, sender: str, content: dict, block_type: str = BLOCK_TYPE_COMMON):
        """Add a new transaction to the mempool or broadcast it to the authority."""
        if self.authority is not None:
            try:
                response = requests.post(
                    f'http://{self.authority}/transaction/create',
                    json=content
                )
                response.raise_for_status()  # Raise an exception for HTTP errors
            except requests.exceptions.RequestException as e:
                print(f"Transaction failed: {e}")
            return

        self.mempool[block_type].append({'sender': sender, 'content': content})

        if len(self.mempool[block_type]) >= FORGE_TRIGGER:
            self.forge(prev_hash=None, curr_hash=None, block_type=block_type)

    def register(self, address: str):
        """Register a new peer node."""
        parsed_url = urlparse(address)
        self.peers.add(parsed_url.path)

    def sync(self) -> bool:
        """Sync blockchain with peer nodes."""
        changed = False
        for peer in self.peers:
            try:
                r = requests.get(f'http://{peer}/')
                if r.status_code != 200:
                    continue

                chain = r.json().get('chain', [])
                if len(chain) > len(self.blocs):
                    self.blocs = chain
                    changed = True
            except requests.exceptions.RequestException as e:
                print(f"Failed to sync with peer {peer}: {e}")
        return changed

    @property
    def previous_block(self) -> dict:
        """Get the last block in the chain."""
        return self.blocs[-1]

    @staticmethod
    def hash(block: dict):
        """Create a SHA-256 hash of a block."""
        to_hash = json.dumps(block)
        return sha256(to_hash.encode()).hexdigest()

    def set_authority(self, address: str):
        """Set a central authority node for the blockchain."""
        self.authority = address


class CryptoVoucher:
    def __init__(self):
        self.base62_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    def validate_hex(self, input_hex, length):
        """Validate if the input is a hex string of a given length."""
        if len(input_hex) != length:
            return False, f"Input must be {length} characters long!"
        if not re.fullmatch(r'[0-9a-fA-F]+', input_hex):
            return False, "Input must be a valid hexadecimal string!"
        return True, None

    def base62_encode(self, hex_input):
        """Convert a hexadecimal string to Base62 encoding."""
        is_valid, error = self.validate_hex(hex_input, 64)
        if not is_valid:
            return None, error

        decimal_value = int(hex_input, 16)
        base62 = ""
        while decimal_value > 0:
            remainder = decimal_value % 62
            base62 = self.base62_chars[remainder] + base62
            decimal_value //= 62

        return base62, None

    def base62_decode(self, base62_input):
        """Convert a Base62-encoded string back to hexadecimal."""
        if not re.fullmatch(r'[0-9A-Za-z]+', base62_input):
            return None, "Invalid Base62 input. Only alphanumeric characters are allowed!"

        decimal_value = 0
        for char in base62_input:
            index = self.base62_chars.index(char)
            decimal_value = decimal_value * 62 + index

        hex_output = f"{decimal_value:064x}"
        return hex_output, None

    def create_voucher(self, private_key):
        """Generate a voucher from a private key using Base62 encoding."""
        base62_encoded, error = self.base62_encode(private_key)
        if error:
            return None, error

        if len(base62_encoded) < 28:
            return None, "Encoded key is too short!"

        voucher_key = base62_encoded[:28]
        voucher_code = base62_encoded[28:]
        return voucher_key, voucher_code

    def restore_private_key(self, voucher_key, voucher_code):
        """Restore the original private key from the voucher key and code."""
        base62_combined = voucher_key + voucher_code
        hex_decoded, error = self.base62_decode(base62_combined)
        if error:
            return None, error
        return hex_decoded, None