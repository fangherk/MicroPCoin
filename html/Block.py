# block.py
# HMC E85 8 December 2017
# hfang@hmc.edu, mjenrungrot@hmc.edu

import hashlib
import hashing
import json

class Block:
    def __init__(self):
        """
        Constructor for block
        """
        self.index = 0                  # block index (first block = 0)
        self.previousHash = "0"         # hash of previous block (first block = 0) (512bits)
        self.timestamp = 0              # POSIX time 
        self.nonce = 0                  # nonce used to identify the proof-of-work step
        self.transactions = []          # list of transactions inside the block
        self.hash = ""                  # hash taken from the contents of the block:
                                        # sha256(index + previousHash + timestamp + nonce + transactions)

    def __repr__(self):
        """
        String representation of block
        """
        # jsonDumper is used for recursively converting an object to correct JSON output format
        def jsonDumper(obj):
            return obj.__dict__
        return json.dumps(self, default=jsonDumper)

    def getDifficulty(self):
        """
        Return difficulty of the block by counting the number of leading zeros.
        """
        return 256 - len('{0:b}'.format(int(self.hash, 16)))

    def toHash(self):
        """
        Compute hash of the block
        """
        nonceBytesString = "{0:08X}".format(self.nonce)
        nonceBytes = bytes([int(nonceBytesString[0:2], 16), int(nonceBytesString[2:4], 16), int(nonceBytesString[4:6], 16),  int(nonceBytesString[6:8], 16)])
        strInput = str(self.index) + str(self.previousHash) + str(self.timestamp) + str(self.transactions)
        strInput = strInput.replace("\"","\'")
        
        print("toHash() BytesString: {:}".format(nonceBytes + strInput.encode('utf-8')))
        return hashlib.sha256(nonceBytes + strInput.encode('utf-8')).hexdigest()

def getGenesis():
    """
    Create a genesis block (the first block).
    """
    block = Block()
    block.index = 0
    block.previousHash = "0"
    block.timestamp = 146515470
    block.nonce = 0
    block.transactions = []
    block.hash = block.toHash()
    return block

def createBlock(data):
    """
    Create a block from JSON object
    """ 
    block = Block()
    block.index = data["index"]
    block.previousHash = data["previousHash"]
    block.timestamp = data["timestamp"]
    block.nonce = data["nonce"]
    block.transactions = data["transactions"]
    block.hash = block.toHash()
    return block
