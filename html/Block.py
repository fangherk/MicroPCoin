import hashlib
import json

class Block:
    def __init__(self):
        self.index = 0                  # block index (first block = 0)
        self.previousHash = ""          # hash of previous block (first block = 0) (512bits)
        self.timestamp = 0              # POSIX time 
        self.nonce = 0                  # nonce used to identify the proof-of-work step
        self.transactions = []          # list of transactions inside the block
        self.hash = ""                  # hash taken from the contents of the block:
                                        # sha256(index + previousHash + timestamp + nonce + transactions)

    def __repr__(self):
        return json.dumps(self.__dict__)

    def getDifficulty(self):
        return int(self.hash, 14)

    def toHash(self):
        strInput = str(self.index) + str(self.previousHash) + str(self.timestamp) + str(self.nonce) + str(self.transactions)
        return hashlib.sha256(strInput.encode('utf-8')).hexdigest()

def getGenesis():
    block = Block()
    block.index = 0
    block.previousHash = "0" * 64
    block.timestamp = 1465154705
    block.nonce = 0
    block.transactions = []
    return block 