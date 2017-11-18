import Block
import pickle

POW_CURVE = 5
EVERY_X_BLOCKS = 5
BASE_DIFFICULTY = 100 # TODO: https://github.com/conradoqg/naivecoin/blob/master/lib/blockchain/index.js

class Blockchain:
    def __init__(self, dbName, transactionsDbName, init=True):
        if init:
            # Create genesis block
            self.blocks = []
            self.transactions = []
            self.blocks.append(Block.getGenesis())
            self.dbName = dbName
            self.transactionsDbName = transactionsDbName
            pickle.dump(self.blocks, open(dbName, "wb"))
            pickle.dump(self.transactions, open(transactionsDbName, "wb"))
        else:
            blockDb = pickle.load(open(dbName, "rb"))
            transactionsDb = pickle.load(open(transactionsDbName, "rb"))
            self.dbName = dbName
            self.transactionsDbName = transactionsDbName

            self.blocks = blockDb
            self.transactions = transactionsDb

    def getAllBlocks(self):
        return self.blocks

    def getBlockByIndex(self, index):
        for block in self.blocks:
            if block.index == index:
                return block
        raise ValueError("Block with index={:} not found".format(index))

    def getBlockByHash(self, hash):
        for block in self.blocks:
            if block.hash == hash:
                return block
        raise ValueError("Block with hash={:} not found".format(hash))
    
    def getLastBlock(self):
        return self.blocks[-1]

    def getDifficulty(self, index):
        """
        TODO: Understand this formula
        https://github.com/conradoqg/naivecoin/blob/master/lib/blockchain/index.js
        """
        return max(int(BASE_DIFFICULTY / ((((index or len(self.blocks)) + 1) // EVERY_X_BLOCKS) ** POW_CURVE)), 0)

    def getAllTransactions(self):
        return self.transactions

    def getTransactionById(self, id):
        for transaction in self.transactions:
            if transaction.id == id:
                return transaction
        raise ValueError("Transaction with id={:} not found".format(id))
    
    def getTransactionFromBlocks(self, transactionId):
        for block in self.blocks:
            for transaction in block.transactions:
                return transaction
        raise ValueError("Transaction with id={:} not found".format(transactionId))

    def replaceChain(self, newChain):
        pass

    def checkChain(self, chain):
        # Check if the genesis block is the same
        if(self.blocks[0] != newChain.blocks[0]):
            raise ValueError("Genesis blocks aren't the same")

        for idx in range(len(chain.blocks) - 1):
            self.checkBlock(chain.blocks[idx+1], chain.blocks[idx])
        
        return True

    def addBlock(self, block):
        if self.checkBlock(block, self.getLastBlock()):
            self.blocks.append(block)
            pickle.dump(self.blocks, open(self.dbName, "wb"))
            self.removeBlockTransactionsFromTransactions(block)
            return block
        else:
            raise ValueError("can't add new block")

    def addTransaction(self, transaction):
        if self.checkTransaction(transaction):
            self.transactions.append(transaction)
            pickle.dump(self.transactions, open(self.transactionsDbName, "wb"))
            return transaction
        else:
            raise ValueError("can't add new transaction")
    
    def removeBlockTransactionsFromTransactions(self, newBlock):
        newtransactions = []
        for transaction in self.transactions:
            found = False
            for transactionBlock in self.newBlock:
                if transaction.id == transactionBlock.id:
                    found = True
                    continue
            if(not found):
                newtransactions.append(transaction)
                
        self.transactions = newtransactions
        pickle.dump(self.transactions, open(self.transactionsDbName, "wb"))
        
        
    def checkBlock(self, newBlock, previousBlock):
        pass

    def checkTransaction(self, transaction):
        pass

    def getUnspentTransactionsForAddress(address):
        pass
    