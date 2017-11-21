import requests
import json 

class Node:
    def __init__(self, host, port, peers, blockchain):
        self.host = host
        self.port = port
        self.peers = peers
        self.blockchain = blockchain
        self.transmitChain()
        self.connectWithPeers(peers)
        

    def __repr__(self):
        """
        String representation of blockchain in JSON format
        """
        # jsonDumper is used for recursively converting an object to correct JSON output format
        def jsonDumper(obj):
            return obj.__dict__
        return json.dumps(self, default=jsonDumper)

    def transmitChain(self):
        # TODO: Find a way to signal an event occurring
        return
        
    def connectWithPeer(self, peer):
        self.connectWithPeers([peer])
        return peer

    def connectWithPeers(self, newPeers):
        """ Connect with the other Raspberry Pi Nodes """
        my_url = "http://{}:{}".format(self.host, self.port)
        for peer in newPeers:
            if peer not in self.peers:
                self.sendPeer(peer, self.host)  # send your own URL
                self.peers.append(peer)         # add the url to the list of peers
                self.initConnection(peer)       # create a connection with the peer
                # self.broadcast(self.sendPeer, peer)
            else:
                print("Peer already added. No more work needed.")
                

    def initConnection(self, peer):
        """ Create a connection with the latest peer """
        self.getLatestBlock(peer)
        self.getTransactions(peer)

    def sendPeer(self, peer, peerToSend):
        """ Tell the other peer that you exist """ 
        base_url = "http://{}:{}/node/peers".format(peer, 5000)
        r = requests.post(base_url, data = {"peer" : peerToSend})
        return r.status_code
    
    def getLatestBlock(self, peer):
        """ Get the latest block from your peer """
        base_url = "http://{}:{}/blockchain/blocks/latest".format(peer, 5000)
        r = requests.get(base_url)
        json_data = r.json()
        self.checkReceivedBlock(json_data[0])
        return json_data[0]

    def sendLatestBlock(self, peer, block):
        """ Send a block to your peer """
        base_url = "http://{}:{}/blockchain/blocks/latest".format(peer, 5000)
        r = requests.put(base_url, data = {"block" : json.dumps(block)})
        print("Sent Latest Block with error message {}".format(r.status_code))
        return r.status_code

    def getBlocks(self, peer):
        """ Get all the blocks from your peer """
        base_url = "http://{}:{}/blockchain/blocks".format(peer, 5000)
        r = requests.get(base_url)
        json_data = r.json()
        for block in json_data:
            self.checkReceivedBlock(block)
        
    def sendTransaction(self, peer, transaction):
        """ Send a transaction from peer to peer using wallet implementation """
        # TODO: Waiting on blockchain transactions
        base_url = "http://{}:{}/blockchain/transactions".format(peer, 5000)
        r = requests.post(base_url, data = {"transaction" : json.dumps(transaction)})
        return r.status_code

    def getTransactions(self, peer):
        """ Get transactions from your peers """
        base_url = "http://{}:{}/blockchain/transactions".format(peer, 5000)
        r = requests.get(base_url)
        json_data = r.json()
        for transaction in json_data:
            self.syncTransactions(transaction)
        print("Done Syncing")

    def getConfirmation(self, peer, transactionID):
        """ Get the confirmation on the transaction ID """
        base_url = "http://{}:{}/blockchain/blocks/transactions/{}".format(peer, 5000, transactionID)
        try:    
            r = requests.get(base_url)
            return True
        except:
            return False

    def getConfirmations(self, transactionID):
        """ Get the confrimation from all of the transactions """
        # TODO: Implement Confirmations from transactions
        transactions = self.blockchain.getTransactionFromBlocks(transactionID)
        numConfirmations = 1
        for peer in self.peers:
            if self.getConfirmation(peer, transactionID):
                numConfirmations += 1

        return numConfirmations

    def syncTransactions(self, transactions):
        """ Add missing transactions """
        for transaction in transactions:
            existent = self.blockchain.getTransactionById(transaction.id)
            if not existent:
                print("Syncing transaction {}", existent["id"])
                self.blockchain.addTransaction(transaction.id)


    def checkReceivedBlock(self, block):
        """ Check the received block """
        return self.checkReceivedBlocks([block])

    def checkReceivedBlocks(self, blocks):
        """ Logic for appending and removing incoming blocks """
        currentBlocks = sorted(blocks, lambda x: x["index"])
        latestBlockReceived = currentBlocks[len(currentBlocks) - 1]
        latestBlockHeld = self.blockchain.getLatestBlock()

        # Don't do anything if the received blockchain is not longer than the actual blockchain
        if latestBlockReceived["index"] <= latestBlockHeld["index"]:
            print("----------------------------------")
            print("Received Block is not long enough!")
            print("----------------------------------")
            return False

        if latestBlockHeld["hash"] == latestBlockReceived["previousHash"]:
            print("Adding the received block to our chain")
            self.blockchain.addBlock(latestBlockReceived)
        elif len(currentBlocks) == 1:
            print("Query chain from peers")
            for peer in self.peers:
                self.getBlocks(peer)
        else: 
            # Received block is longer than current chain, so replace it
            self.blockchain.replaceChain(currentBlocks)

            
            
            

