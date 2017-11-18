class Block:
    def __init__(self):
        self.index = 0                  # block index (first block = 0)
        self.previousHash = ""          # hash of previous block (first block = 0) (512bits)
        self.timestamp = 0              # POSIX time 
        self.nonce = 0                  # nonce used to identify the proof-of-work step
        self.transactions = []          # list of transactions inside the block
        self.hash = ""                  # hash taken from the contents of the block:
                                        # sha256(index + previousHash + timestamp + nonce + transactions)

    def getGenesis(self):
        self.index = 0
        self.previousHash = "0" * 64
        self.timestamp = 1465154705
        self.nonce = 0
        self.transactions = []
        return self 