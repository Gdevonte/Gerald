class Blockchain:
    def __init__(self):
        self.chain = []
        self.mempool = []
        self.mining_reward = 50  # 50 XKW

    def mine_block(self, miner_address):
        block = {
            'transactions': self.mempool,
            'previous_hash': self.get_last_block_hash(),
            'nonce': self.proof_of_work(self.get_last_proof())
        }
        self.chain.append(block)
        self.mempool = [{'sender': 'network', 'recipient': miner_address, 'amount': self.mining_reward}]

    def adjust_difficulty(self):
        # This is a simplified example. Implement actual logic based on your requirements.
        if len(self.chain) % 10 == 0:
            self.difficulty += 1
        elif len(self.chain) % 15 == 0:
            self.difficulty -= 1
