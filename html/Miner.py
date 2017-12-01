import Block
import Transaction
import hashing
import time
import secrets
import threading
import queue
import sys

FEE_PER_TRANSACTION = 1
MINING_REWARD = 5000000000


class Miner:
    def __init__(self, blockchain, logLevel):
        """
        Constructor for a miner
        """
        self.blockchain = blockchain
        self.logLevel = logLevel
        self.threadQueue = queue.Queue()

    def mine(self, address):
        """
        Wrapper function mining. The reward will be added to the specified when mining a block is done.
        """
        # Create a base block with important information based on the previous block (e.g. hash, etc.)
        baseBlock = self.generateNextBlock(address, self.blockchain.getLastBlock(), self.blockchain.transactions)

        print("base block:\n", baseBlock)
        print("base block difficulty:\n", baseBlock.getDifficulty())
        # Spawn a thread to perform proof-of-work and wait for output.
        # Wait for the thread to finish before moving on.
        thr = threading.Thread(target=self.proveWorkFor, args=(baseBlock, self.blockchain.getDifficulty(baseBlock.index),))
        thr.start()
        thr.join()

        # Collect the output from the created thread
        output = self.threadQueue.get()
        return output


    def generateNextBlock(self, address, previousBlock, blockchainTransactions):
        """
        Create a next block based on its previous block.

        address - The address for the reward of mining
        previousBlock - Block.Block() object of the previous block
        blockchainTransactions - list of all pending transactions
        """

        # The index of the new block must be one after its previous block
        index = previousBlock.index + 1

        # Get the hash of its previous block
        previousHash = previousBlock.hash

        # Get the current timestamp
        timestamp = int(time.time())

        # Get the first 2 pending transactions
        transactions = []
        if len(blockchainTransactions) >= 1:
            transactions.append(blockchainTransactions[0])

        if len(blockchainTransactions) >= 2:
            transactions.append(blockchainTransactions[1])
        
        # Add fee transaction based on the number of transactions processed
        if len(transactions) > 0:
            data = {}
            data["id"] = secrets.token_hex(32) # 64-characters
            data["hash"] = None
            data["type"] = "fee"
            data["data"] = {
                "inputs": [],
                "outputs": [{
                    "amount": FEE_PER_TRANSACTION * len(transactions),
                    "address": address
                }]
            }
            feeTransaction = Transaction.createTransaction(data)
            transactions.append(feeTransaction)

        # Add reward transaction 
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
            transactions.append(rewardTransaction)

        # Create a block intended to put to the blockchain
        # Note that nonce field will be dealt later in the proof-of-work process.
        return Block.createBlock({"index": index,
                                  "nonce": 0,
                                  "previousHash": previousHash,
                                  "timestamp": timestamp,
                                  "transactions": transactions
                                })

    def proveWorkFor(self, jsonBlock, difficulty):
        """
        Perform the proof-of-work by changing nonce field.
        """
        blockDifficulty = None
        block = Block.createBlock(jsonBlock.__dict__)

        while True:
            # Get the timestamp
            block.timestamp = int(time.time())

            # Change the nonce
            block.nonce += 1

            # Recalculate the hash
            strInput = str(block.index) + str(block.previousHash) + str(block.timestamp) + str(block.nonce) + str(block.transactions)
            strInput = strInput.replace("\"", "\'")
            # strInput = str(block.index)  + str(block.previousHash) + str(block.timestamp) + str(block.nonce) + str(block.transactions)
            print("strInput: \t", strInput)
            block.hash = hashing.get_spi(strInput)
            print("\npi hash\n")
            print(block.hash)
            print("\n\n")
            print(" hash calculation\n")
            print(block.toHash())
            print("\n\n")
            # block.hash = block.toHash()

            # Recompute the difficulty of the block
            blockDifficulty = block.getDifficulty()
            print("INFO: blockDifficulty={:} chainDifficulty={:}".format(blockDifficulty, difficulty), file=sys.stderr)

            # Once the block difficulty exceeds the required difficulty, we have proved the block.
            if blockDifficulty > difficulty: break

        # Output back to the wrapper function call
        print("Mined block = {:}".format(str(block)), file=sys.stderr)
        self.threadQueue.put(block)
        return block
