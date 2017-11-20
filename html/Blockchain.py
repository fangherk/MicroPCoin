import Block
import pickle
import json

POW_CURVE = 5
EVERY_X_BLOCKS = 5
BASE_DIFFICULTY = 9007199254740991  # Maximum Safe Integer for Javascript
MINING_REWARD = 5000000000

class Blockchain:
    def __init__(self, dbName, transactionsDbName, init=True):
        """
        Constructor for a blockchain
        """
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
            # Create a blockchain from given files
            blockDb = pickle.load(open(dbName, "rb"))
            transactionsDb = pickle.load(open(transactionsDbName, "rb"))
            self.dbName = dbName
            self.transactionsDbName = transactionsDbName
            self.blocks = blockDb
            self.transactions = transactionsDb

    def __repr__(self):
        """
        String representation of blockchain in JSON format
        """
        return json.dumps(self.__dict__)
    
    def getAllBlocks(self):
        """
        Return all blocks inside the blockchain
        """
        return self.blocks

    def getBlockByIndex(self, index):
        """
        Return a block specified by the index (integer)

        If the block is not found, ValueError() is raised.
        """
        for block in self.blocks:
            if block.index == index:
                return block
        raise ValueError("Block with index={:} not found".format(index))

    def getBlockByHash(self, hash):
        """
        Return a block specified by the hash (string)

        If the block is not found, ValueError() is raised.
        """
        for block in self.blocks:
            if block.hash == hash:
                return block
        raise ValueError("Block with hash={:} not found".format(hash))
    
    def getLastBlock(self):
        """
        Return the latest block
        """
        return self.blocks[-1]

    def getDifficulty(self, index):
        """
        Calculate the difficulty based on the index. The difficulty should increase as the number 
        of index increases.

        Note: This formula is taken from 
        https://github.com/conradoqg/naivecoin/blob/master/lib/blockchain/index.js
        """
        return max(int(BASE_DIFFICULTY / (((((index or len(self.blocks)) + 1) // EVERY_X_BLOCKS) + 1) ** POW_CURVE)), 0)

    def getAllTransactions(self):
        """
        Return list of all pending transactions 
        """
        return self.transactions

    def getTransactionById(self, id):
        """
        Return a pending transaction by id.abs
        
        If the transaction is not found, ValueError() is raised.
        """
        for transaction in self.transactions:
            if transaction.id == id:
                return transaction
        raise ValueError("Transaction with id={:} not found".format(id))
    
    def getTransactionFromBlocks(self, transactionId):
        """
        Return a transaction from all blocks
        
        If the transaction is not found, ValueError() is raised.
        """
        for block in self.blocks:
            for transaction in block.transactions:
                return transaction
        raise ValueError("Transaction with id={:} not found".format(transactionId))

    def replaceChain(self, newChain):
        """
        Replace a current blockchain with the new blockchain. This is done by 
        finding the block that starts to diverge. Then, replace all blocks after diversion.

        If the new blockchain is shorter than the current one, ValueError() is raised.
        """

        # Check the length of new blockchain whether it's valid.
        if(len(newChain.blocks) <= len(self.blocks)):
            raise ValueError("New blockchain is shorter than the current blockchain")

        # Check that blocks inside the new blockchain are valid.
        self.checkChain(newChain)

        # Replace blocks after diversion.
        lastN = len(newChain.blocks) - len(self.blocks)
        newBlocks = newChain.blocks[-lastN:]
        for blockToAdd in newBlocks:
            self.addBlock(blockToAdd)
            
        # TODO: send signal saying that the blockchain has been replaced.

    def checkChain(self, chain):
        """
        Check if the input blockchain is valid. 
        """
        # Check if the genesis block is the same
        if(self.blocks[0] != chain.blocks[0]):
            raise ValueError("Genesis blocks aren't the same")

        # Check that every two consecutive blocks' hash and previousHash are valid
        for idx in range(len(chain.blocks) - 1):
            self.checkBlock(chain.blocks[idx+1], chain.blocks[idx])
        
        return True

    def addBlock(self, block):
        """
        Add a block to the blockchain. Then, save to the blockchain database.

        If the new block is not valid, ValueError() is raised.
        """
        if self.checkBlock(block, self.getLastBlock()):
            self.blocks.append(block)
            pickle.dump(self.blocks, open(self.dbName, "wb"))
            self.removeBlockTransactionsFromTransactions(block)
            return block
        else:
            raise ValueError("can't add new block")

    def addTransaction(self, transaction):
        """
        Add a transaction to the list of pending transactions. Then, svae to the
        pending transaction database. 

        If the new transaction is not valid, ValueError() is raised.
        """
        if self.checkTransaction(transaction):
            self.transactions.append(transaction)
            pickle.dump(self.transactions, open(self.transactionsDbName, "wb"))
            return transaction
        else:
            raise ValueError("can't add new transaction")
    
    def removeBlockTransactionsFromTransactions(self, newBlock):
        """
        Remove all transactions in the new block from the list of pending transactions.
        """

        newtransactions = []
        # Remove any transaction in the pending transaction list that is in the new block.
        for transaction in self.transactions:
            found = False
            for transactionBlock in newBlock:
                if transaction.id == transactionBlock.id:
                    found = True
                    continue
            if(not found):
                newtransactions.append(transaction)

        # Update transactions object and write to the database
        self.transactions = newtransactions
        pickle.dump(self.transactions, open(self.transactionsDbName, "wb"))
        
        
    def checkBlock(self, newBlock, previousBlock):
        """
        Check that the new block is valid based on its previous block.
        """
        
        # Re-calculate the hash of the new block
        newBlockHash = newBlock.toHash()

        if(previousBlock.index + 1 != newBlock.index):
            raise ValueError("Expect new block of id = previous id + 1")
        if(previousBlock.hash != newBlock.previousHash):
            raise ValueError("Expect new block's previous hash to match newBlock.previousHash={:}, previousBlock.hash={:}".format(newBlock.previousHash, previousBlock.hash))
        if(newBlock.hash != newBlockHash):
            raise ValueError("Expect new block's hash to match the calculation")
        if(newBlock.getDifficulty() >= self.getDifficulty(newBlock.index)):
            raise ValueError("Expect new block's difficulty to be smaller \
                              [newBlock.diif = {:}] [{:}]".format(newBlock.getDifficulty(), self.getDifficulty(newBlock.index)))

        # Check that all transacations are valid
        for transaction in newBlock.transactions:
            self.checkTransaction(transaction)

        # Check the sum of input transactions and output transactions to/from block.
        # The sum of input transactions must be greter than or equal to the sum of 
        # output transactions.
        sumOfInputsAmount = 0
        sumOfOutputsAmount = 0
        nfeeTransactions = 0
        nrewardTransactions = 0
        for transaction in newBlock.transactions:
            nfeeTransactions += (transaction.type == "fee")
            nrewardTransactions += (transaction.type == "reward")
            for inputTransaction in transaction.data["inputs"]:
                sumOfInputsAmount += inputTransaction["amount"]
            for outputTransaction in transaction.data["outputs"]:
                sumOfOutputsAmount += outputTransaction["amount"]

        sumOfInputsAmount += MINING_REWARD
        if(sumOfInputsAmount < sumOfOutputsAmount):
            raise ValueError("Expect sum of input transactions to be greater than the sum of output transactions, inputSum={:}, outputSum={:}".format(sumOfInputsAmount, sumOfOutputsAmount))

        if(nfeeTransactions > 1):
            raise ValueError("Expect to have only 1 fee transaction")      
        
        if(nrewardTransactions > 1):
            raise ValueError("Expect to have only 1 reward transaction")

        return True

    def checkTransaction(self, transaction):
        """
        Check that the new transaction is valid based on the blockchain, e.g. not already in the blockchain.
        """
        # Check that the transaction, in terms of signature, etc.
        transaction.check()

        # Check if the transaction is already in the blockchain.
        for each in self.transactions:
            if(each.id == transaction.id):
                raise ValueError("New transaction is already existed in the blockchain")
        
        # Check if the transaction is already spent
        for inputTransaction in transaction.data["inputs"]:
            for block in self.blocks:
                for previousTransaction in block.transacations.data["input"]:
                    if(inputTransaction["index"] == previousTransaction["index"] and\
                       inputTransaction["transaction"] == previousTransaction["transaction"]):
                       raise ValueError("transaction is already spent")

        return True

    def getUnspentTransactionsForAddress(self, address):
        """
        Return a list of all unspent transaction identified by the given address.
        """
        inputs = []
        outputs = []
        # Obtain a list of input/output transactions for the given address
        for block in self.blocks:
            for transaction in block.transactions:
                idx = 0
                for transactionOutput in transaction.data["outputs"]:
                    if transactionOutput["address"] == address:
                        transactionOutput["transaction"] = transaction.id;
                        transactionOutput["index"] = idx
                        outputs.append(transactionOutput)
                        idx += 1
                for transactionInput in transaction.data["inputs"]:
                    if transactionInput["address"] == address:
                        inputs.append(transactionInput)
            
        # Remove any output transaction that is also in the input transactions' list.
        unspentTransactionOutput = []
        for outputTransaction in outputs:
            found = False
            for inputTransaction in inputs:
                if(inputTransaction["transaction"] == outputTransaction["transaction"] and \
                   inputTransaction["index"] == outputTransaction["index"]):
                   found = True
                   break
            if(not found):
                unspentTransactionOutput.append(outputTransaction)
        return unspentTransactionOutput
        
    
