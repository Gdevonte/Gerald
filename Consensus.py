import hashlib
import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.mempool = []
        self.difficulty = 4  # Adjust difficulty level

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
