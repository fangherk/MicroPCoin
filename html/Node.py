import requests

class Node:
    def __init__(self, host, port, peers, blockchain):
        self.host = host
        self.port = port
        self.peers = []
        self.blockchain = blockchain
        self.transmitChain()
        self.connectWithPeers()

    def transmitChain(self):
        # TODO: Find a way to signal an event occurring
        return
        
    def connectWithPeers(self):
        """ Connect with the other Raspberry Pi Nodes """
        my_url = "http://{}:{}".format(self.host, self.port)
        for peer in self.peers:
            if peer.url != my_url:
                self.sendPeer(peer, {"url": my_url})
                self.peers.append(peer)
                self.initConnection(peer)
                self.broadcast(self.sendPeer, peer)
            else:
                print("Peer already added. No more work needed.")
                

    def initConnection(self, peer):
        """ Create a connection with the latest peer """
        self.getLatestBlock(peer)
        self.getTransactions(peer)

    def sendPeer(self, peer, peerToSend):
        """ Tell the other peer that you exist """ 
        base_url = "{}/node/peers".format(peer)
        r = requests.post(base_url, data = {"peer" : peerToSend})
        return r.status_code
    
    def getLatestBlock(self, peer):
        """ Get the latest block from your peer """
        base_url = "{}/blockchain/blocks/latest".format(peer)
        r = requests.get(base_url)
        return r.json()

    def sendLatestBlock(self, peer, block):
        """ Send a block to your peer """
        # TODO: Jsonify block data?
        base_url = "{}/blockchain/blocks/latest".format(peer)
        r = requests.put(base_url, data = {"block" : block})
        return r.status_code

    def getBlocks(self, peer):
        """ Get all the blocks from your peer """
        base_url = "{}/blockchain/blocks".format(peer)
        r = requests.get(base_url)
        return r.json()

    def sendTransaction(self, peer, transaction):
        """ Send a transaction from peer to peer using wallet implementation """
        # TODO: Jsonify transaction data?
        base_url = "{}/blockchain/transactions".format(peer)
        r = requests.post(base_url, data = {"transaction" : transaction})
        return r.status_code

    def getTransactions(self, peer):
        """ Get transactions from your peers """
        base_url = "{}/blockchain/transactions".format(peer)
        r = requests.get(base_url)
        return r.json()

    def getConfirmation(self, peer, transactionID):
        """ Get the confirmation on the transaction ID """
        # TODO: Implement Boolean Logic from json
        base_url = "{}/blockchain/transactions/{}".format(peer, transactionID)
        r = requests.get(base_url)
        
        return True

    def getConfirmations(self, peer, transactionID):
        """ Get the confrimation from all of the transactions """
        # TODO: Implement Confirmations from transactions
        transactions = self.blockchain.getTransactionFromBlocks(transactionID)
        totalConfirmation = True
        for peer in self.peers:
            if getConfirmation(peer):
                return False

    def syncTransactions(self, transactions):
        """ Add missing transactions """
        for transaction in transactions:
            existent = self.blockchain.getTransactionById(transaction.id)
            if not existent:
                self.blockchain.addTransaction(transaction.id)


    def checkReceivedBlock(self, block):
        """ Check the received block """
        return self.checkReceivedBlocks([block])

    def checkReceivedBlocks(self, blocks):
        """ Logic for appending and removing incoming blocks """
        # TODO: Double check implementation
        currentBlocks = sorted(blocks, lambda x: x["index"])
        latestBlockReceived = currentblocks[len(currentBlocks) - 1]
        latestBlockHeld = self.blockchain,getLatestBlock()

        if latestBlockReceived["index"] <= latestBlockHeld["index"]:
            print("Received Block is not long enough")
        if latestBlockHeld["hash"] == latestBlockReceived["previousHash"]:
            self.blockchain.addBlock(latestBlockReceived)
        elif len(currentBlocks) == 1:
            for peer in self.peers:
                self.getBlocks(peer)
        else: 
            self.blockchain.replaceChain(currentBlocks)

            
            
            

