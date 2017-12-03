import requests
import Blockchain
import Transaction
import Block
import json 
import os

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
        """
        On event signals, transmit data to other peers
        """
        @self.blockchain.ee.on("replacedBlockchain")
        def data_handler(data):
            if self.peers:
                for peer in self.peers:
                    self.sendLatestBlock(peer, data[-1])
            else:
                print("No peers to send to")
        @self.blockchain.ee.on("addedBlock")
        def data_handler(data):
            #print(type(data))
            #print(data)
            if self.peers:
                for peer in self.peers:
                    self.sendLatestBlock(peer, data)
            else: 
                print("No peers to send to")
        @self.blockchain.ee.on("addedTransaction")
        def data_handler(data):
            if self.peers:
                for peer in self.peers:
                    self.sendTransaction(peer, data)
            else:
                print("No peers to send to")
        return
        
    def connectWithPeer(self, peer):
        self.connectWithPeers([peer])
        return peer

    def connectWithPeers(self, newPeers):
        """ Connect with the other Raspberry Pi Nodes """
        my_url = "http://{}:{}".format(self.host, self.port)
        for peer in newPeers:
            if (peer not in self.peers) and (peer != os.environ["ip"]):
                self.peers.append(peer)         # add the url to the list of peers
                self.sendPeer(peer, self.host)  # send your own URL
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
        base_url = "http://{:}:{:}/node/peers".format(peer, 5000)
        headers = {'Content-Type' : 'application/json'}
        print("does it hang? \n\n\n")
        peerDict = {"peer" : peerToSend}
        r = requests.post(base_url, data = json.dumps(peerDict), headers =headers)
        print("yeah buddy? \n\n\n")
        return r.status_code
    
    def getLatestBlock(self, peer):
        """ Get the latest block from your peer """
        base_url = "http://{}:{}/blockchain/blocks/latest".format(peer, 5000)
        r = requests.get(base_url)
        json_data = r.json()
        received_block = Block.createBlock(json_data) 
        self.checkReceivedBlock(received_block)
        return json_data

    def sendLatestBlock(self, peer, block):
        """ Send a block to your peer """
        base_url = "http://{}:{}/blockchain/blocks/latest".format(peer, 5000)

        # print("block\n", block)
        json_output = {}
        json_output["index"] = block.index
        json_output["previousHash"] = block.previousHash
        json_output["timestamp"] = block.timestamp
        json_output["nonce"] = block.nonce
        

        temp_transactions = []
        for transaction in block.transactions:
            try: 
                temp_transactions.append(transaction.__dict__)
            except:
                temp_transactions.append(transaction)
        json_output["transactions"] = temp_transactions
        
        print("\njson_output\n", json_output)

        headers = {'Content-Type' : 'application/json'}
         
        r = requests.put(base_url, data = json.dumps(json_output), headers = headers)
        print("\n")
        print("Sent Latest Block with error message {}".format(r.status_code))
        return r.status_code

    def getBlocks(self, peer):
        """ Get all the blocks from your peer """
        base_url = "http://{}:{}/blockchain/blocks".format(peer, 5000)
        r = requests.get(base_url)
        json_data = r.json()
        
        blocks = []
        for block in json_data:
            block = Block.createBlock(block)
            blocks.append(block)

        self.checkReceivedBlocks(blocks)
        
    def sendTransaction(self, peer, transaction):
        """ Send a transaction from peer to peer using wallet implementation """
        base_url = "http://{}:{}/blockchain/transactions".format(peer, 5000)
        headers = {'Content-Type' : 'application/json'}
        r = requests.post(base_url, data = json.dumps(transaction.__dict__), headers=headers)
        return r.status_code

    def getTransactions(self, peer):
        """ Get transactions from your peers """
        base_url = "http://{}:{}/blockchain/transactions".format(peer, 5000)
        r = requests.get(base_url)
        json_data = r.json()
        transactions = []
        for transaction in json_data:
            transaction = Transaction.createTransaction(transaction)
            transactions.append(transaction)
        self.syncTransactions(transactions)
        print("Done Syncing")

    def getConfirmation(self, peer, transactionID):
        """ Get the confirmation on the transaction ID """
        base_url = "http://{}:{}/blockchain/blocks/transactions/{}".format(peer, 5000, transactionID)
        try:
            r = requests.get(base_url)
            return r.json()
        except:
            # maybe this could be None
            return "Error"


    def getConfirmations(self, transactionID):
        """ Get the confrimation from all of the transactions """
        transactions = self.blockchain.getTransactionFromBlocks(transactionID)
        numConfirmations = 1
        for peer in self.peers:
            if self.getConfirmation(peer, transactionID):
                numConfirmations += 1

        return numConfirmations

    def syncTransactions(self, transactions):
        """ Add missing transactions """
        for transaction in transactions:
            existent = None
            try:
                existent = self.blockchain.getTransactionById(transaction.id)
            except ValueError:
                print("Syncing transaction {}", transaction.id)
                self.blockchain.addTransaction(transaction)


    def checkReceivedBlock(self, block):
        """ Check the received block """
        return self.checkReceivedBlocks([block])

    def checkReceivedBlocks(self, blocks):
        """ Logic for appending and removing incoming blocks """
        currentBlocks = sorted(blocks, key=lambda x: x.index)
        latestBlockReceived = currentBlocks[len(currentBlocks) - 1]
        latestBlockHeld = self.blockchain.getLastBlock()

        # Don't do anything if the received blockchain is not longer than the actual blockchain
        if latestBlockReceived.index <= latestBlockHeld.index:
            print("----------------------------------")
            print("Received Block is not long enough!")
            print("----------------------------------")
            return False

        if latestBlockHeld.hash == latestBlockReceived.previousHash:
            print("Adding the received block to our chain")
            self.blockchain.addBlock(latestBlockReceived)
        elif len(currentBlocks) == 1:
            print("Query chain from peers")
            for peer in self.peers:
                self.getBlocks(peer)
        else: 
            # Received block is longer than current chain, so replace it
            newBlockchain = Blockchain.createBlockchain(self.blockchain, currentBlocks)
            self.blockchain.replaceChain(newBlockchain)

            
            
            

