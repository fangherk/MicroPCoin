""" Library Imports """
from flask import Flask, jsonify, request
from flask.json import loads

import os
import hashlib
import json
import Block
import Blockchain
import Operator
import Transaction
import Miner
import Node


import ed25519

""" --------------- """
""" --------------- """

uPCoin = Flask(__name__)
blockchain = Blockchain.Blockchain("blockchainDb", "transactionDb")
operator = Operator.Operator('walletDb', blockchain)
miner = Miner.Miner(blockchain, None)
node = Node.Node(os.environ["ip"], os.environ["port"], [], blockchain)

""" Main Page """
@uPCoin.route('/')
def index():
    # TODO: Prettify This Page
    return 'Welcome to uPCoin.'


""" Blockchain GET/POST requests """

@uPCoin.route('/blockchain/blocks', methods=['GET'])
def get_blocks():
    """ Return all blocks in JSON format """
    return str(blockchain.getAllBlocks())

@uPCoin.route('/blockchain/blocks/latest', methods=['GET', 'PUT'])
def latest_blocks():
    """ GET: Return the latest block in JSON format
        PUT: Adda block to the blockchain """ 
    if request.method == 'GET':
        return str(blockchain.getLastBlock())
    elif request.method == 'PUT':
        print("I get here")
        print(request.json)
        # Take in the request
        inputJSON = request.json

        # Create a block for the request
        blockToAdd = Block.Block()
        blockToAdd.index = inputJSON["index"]
        blockToAdd.previousHash = inputJSON["previousHash"]
        blockToAdd.timestamp = inputJSON["timestamp"]
        blockToAdd.nonce = inputJSON["nonce"]
        blockToAdd.transactions = inputJSON["transactions"]
        blockToAdd.hash = blockToAdd.toHash()

        # Add block
        return str(blockchain.addBlock(blockToAdd))

@uPCoin.route('/blockchain/blocks/hash/<hash_val>', methods=['GET'])
def get_block_by_hash(hash_val):
    """ Return a block by its specified hash """
    if request.method == 'GET':
        return str(blockchain.getBlockByHash(hash_val))

@uPCoin.route('/blockchain/blocks/index/<index_val>', methods=['GET'])
def get_block_by_index(index_val):
    """ Return a block by its specified index """
    if request.method == 'GET':
        index_val = int(index_val)
        return str(blockchain.getBlockByIndex(index_val))

@uPCoin.route('/blockchain/blocks/transactions/<transactionId_val>', methods=['GET'])
def get_transaction(transactionId_val):
    """ Return the latest transaction by its id """
    if request.method == 'GET':
        return str(blockchain.getTransactionById(transactionId_val))
    
@uPCoin.route('/blockchain/transactions', methods=['GET', 'POST'])
def transaction(transactionId_val=None):
    """ GET: Return the latest transactions
        POST: Add a transaction """
    if request.method == 'GET':
        return str(blockchain.getAllTransactions())
    elif request.method == 'POST':
        transaction = Transaction.createTransaction(request.json)
        return str(blockchain.addTransaction(transaction))

@uPCoin.route('/blockchain/transactions/unspent/<address>', methods=['GET'])
def get_unspent_transactions(address):
    """ Get the unspent transactions for the address. """
    if request.method == 'GET':
        unspentTransaction = blockchain.getUnspentTransactionsForAddress(address)
        return str(json.dumps(unspentTransaction))

"""
Operator
"""

@uPCoin.route('/operator/wallets', methods=['GET', 'POST'])
def wallets():
    """ GET: Get all wallets 
        POST: Create a new Wallet by posting a password """
    if request.method == 'GET':
        return str(operator.getWallets())
    elif request.method == "POST":
        jsonData = json.loads(request.data)
        password = jsonData["password"]
        createdWallet = operator.createWalletFromPassword(password)

        # Create a wallet representation that hides the secret and passwordHash
        walletRepresentation = {}
        walletRepresentation["id"] = createdWallet.id
        walletRepresentation["keypairs"] = createdWallet.keypairs
        return str(json.dumps(walletRepresentation))

@uPCoin.route('/operator/wallets/<walletId>', methods=['GET'])
def getWalletById(walletId):
    """ Get a wallet by the specified ID """
    if request.method == "GET":
        return str(operator.getWalletById(walletId))

@uPCoin.route('/operator/wallets/<walletId>/transactions', methods=['POST'])
def createTransaction(walletId):
    """ Create a Transaction """
    if request.method == "POST":
        # Obtain relevant data:
        #   password, fromAddress, toAddress, amount, changeAddress
        jsonData = json.loads(request.data)
        password = jsonData["password"]
        fromAddress = jsonData["from"]
        toAddress = jsonData["to"]
        amount = jsonData["amount"]
        changeAddress = jsonData["changeAddress"]
        # Compute the hash of the provided password
        passwordHash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        # Check if the password hash is the same with the stored password hash
        if not operator.checkWalletPassword(walletId, passwordHash):
            # TODO: Change to 403 Error
            return "Error"

        # Create a transaction 
        newTransaction = operator.createTransaction(walletId, fromAddress, toAddress, amount, changeAddress)
        
        # Check if the transaction is signed correctly
        newTransaction.check()

        # Add thte transaction to the list of pending transaction
        transcationCreated = blockchain.addTransaction(Transaction.createTransactionObject(newTransaction))

        return str(transcationCreated)

@uPCoin.route('/operator/wallets/<walletId>/addresses', methods=['GET', 'POST'])
def addressesWallet(walletId):
    """ GET: Get all address of a wallet
        POST: Create a new address for a wallet """
    if request.method == "GET":
        # Get all addresses of a wallet
        return str(operator.getAddressesForWallet(walletId))
    elif request.method == "POST":
        # Create a new address

        # Obtain relevant data:
        #   password
        jsonData = json.loads(request.data)
        password = jsonData["password"]

        # Compute the hash of the provided password
        passwordHash = hashlib.sha256(password.encode('utf-8')).hexdigest()

         # Check if the password hash is the same with the stored password hash
        if not operator.checkWalletPassword(walletId, passwordHash):
            # TODO: Change to 403 Error
            return "Error"

        newAddress = operator.generateAddressForWallet(walletId)
        return str(json.dumps({"address": newAddress}))


@uPCoin.route('/operator/wallets/<walletId>/addresses/<addressId>/balance', methods=['GET'])
def getBalance(walletId, addressId):
    """ Get the balance of a wallet """
    if request.method == "GET":
        # Get a balance for the specified addressId and walletId
        balance = operator.getBalanceForAddress(addressId)
        return str(json.dumps({"balance": balance}))

"""
Node
"""
@uPCoin.route('/node/peers', methods=['GET', 'POST'])
def peers():
    """ Find the nodes of a peer """
    if request.method == 'GET':
        return str(node.peers)
    elif request.method == "POST":
        jsonData = json.loads(request.data)
        newPeer = node.connectWithPeer(jsonData["peer"])
        return str(newPeer)


@uPCoin.route('/node/transactions/<transactionId>/confirmations', methods=['GET'])
def getComfirmations(transactionId):
    if request.method == 'GET':
        numConfirmations = node.getConfirmations(transactionId)
    return str(json.dumps({"confirmations" : numConfirmations}))

"""
Miner
"""
@uPCoin.route('/miner/mine', methods=['POST'])
def mine():
    """ Mine a new block """ 
    if request.method == 'POST':
        # Obtain relevant data:
        #   rewardAddress
        jsonData = json.loads(request.data)
        rewardAddress = jsonData["rewardAddress"]

        # Mine with the reward address
        newBlock = miner.mine(rewardAddress)

        # When this function call succeeds, it adds the block to the blockchain
        blockchain.addBlock(newBlock);

        # Output the just created block
        return str(newBlock)


if __name__=='__main__':
    uPCoin.run(debug=True, host=os.environ["ip"])
