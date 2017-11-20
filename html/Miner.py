import Block
import Transaction
import time
import secrets

FEE_PER_TRANSACTION = 1
MINING_REWARD = 5000000000

class Miner:
    def __init__(self, blockchain, logLevel):
        self.blockchain = blockchain
        self.logLevel = logLevel

    def mine(self, address):
        baseBlock = self.generateNextBlock(address, self.blockchain.getLastBlock(), self.blockchain.transactions)

    def generateNextBlock(self, address, previousBlock, blockchainTransactions):
        index = previousBlock.index + 1
        previousHash = previousBlock.previousHash
        timestamp = int(time.time())

        transactions = []
        if len(blockchainTransactions) >= 2:
            transactions[0] = blockchainTransactions[0]
            transactions[1] = blockchainTransactions[1]
        
        if len(transactions) > 0:
            data = {}
            data["id"] = secrets.token_hex(32) # 64-characters
            data["hash"] = None
            data["type"] = "fee"
            data["data"] = {
                "inputs": [],
                "outputs": [{
                    "amount": FEE_PER_TRANSACTION,
                    "address": address
                }]
            }
            feeTransaction = Transaction.createTransaction(data)
            transactions.push(feeTransaction)

        # Rewrad transaction
        if address != None:
            data = {}
            data["id"] = secrets.token_hex(32) # 64-characters
            data["hash"] = None
            data["type"] = "reward"
            data["data"] = {
                "inputs": [],
                "outputs": [{
                    "amount": MINING_REWARD,
                    "address": address
                }]
            }
            rewardTransaction = Transaction.createTransaction(data)
            transactions.push(rewardTransaction)

        return Block.createBlock({"index": index,
                                  "nonce": 0,
                                  "previousHash": previousHash,
                                  "timestamp": timestamp,
                                  "transactions": transactions
                                })

    def proveWorkFor(self, jsonBlock, difficulty):
        blockDifficulty = None
        block = Block.createBlock(jsonBlock)

        while True:
            block.timestamp = int(time.time())
            block.nonce += 1
            block.hash = block.toHash()
            blockDifficulty = block.getDifficulty()
            if blockDifficulty < difficulty: break

        return block