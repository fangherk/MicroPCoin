import hashlib
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
        Return difficulty of the block
        """
        return int(self.hash[:13], 16)

    def toHash(self):
        """
        Compute hash of the block
        """
        strInput = str(self.index) + str(self.previousHash) + str(self.timestamp) + str(self.nonce) + str(self.transactions)
        return hashlib.sha256(strInput.encode('utf-8')).hexdigest()

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