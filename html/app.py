""" Library Imports """
from flask import Flask, jsonify, request
from flask.json import loads

import os
import hashlib
import json
import Block
import Blockchain
import Operator
import Miner
import Node



""" --------------- """
""" --------------- """

uPCoin = Flask(__name__)
blockchain = Blockchain.Blockchain("blockchainDb", "transactionDb")
operator = Operator.Operator('walletDb', blockchain)
miner = Miner.Miner(blockchain, None)
node = Node.Node(os.environ["ip"], os.environ["port"], ["142.129.183.125"], blockchain)

""" Main Page """
@uPCoin.route('/')
def index():
    return 'Welcome to uPCoin.'


""" Blockchain GET/POST requests """

@uPCoin.route('/blockchain/blocks', methods=['GET'])
def get_blocks():
    # Return all blocks in JSON format
    return str(blockchain.getAllBlocks())

@uPCoin.route('/blockchain/blocks/latest', methods=['GET', 'PUT'])
def latest_blocks():
    if request.method == 'GET':
        # Return latest block in JSON format
        return str(blockchain.getLastBlock())
    elif request.method == 'PUT':
        # Parse the JSON Put Request and add it to the blockchain
        inputJSON = request.json
        blockToAdd = Block.Block()
        blockToAdd.index = inputJSON["index"]
        blockToAdd.previousHash = inputJSON["previousHash"]
        blockToAdd.timestamp = inputJSON["timestamp"]
        blockToAdd.transactions = inputJSON["transactions"]
        blockToAdd.hash = blockToAdd.toHash()
        return str(blockchain.addBlock(blockToAdd))

@uPCoin.route('/blockchain/blocks/hash/<hash_val>', methods=['GET'])
def get_block_by_hash(hash_val):
    # Return a block with specified hash
    if request.method == 'GET':
        return str(blockchain.getBlockByHash(hash_val))

@uPCoin.route('/blockchain/blocks/index/<index_val>', methods=['GET'])
def get_block_by_index(index_val):
    # Return a block with specified index
    if request.method == 'GET':
        index_val = int(index_val)
        return str(blockchain.getBlockByIndex(index_val))

@uPCoin.route('/blockchain/blocks/transactions/<transactionId_val>', methods=['GET'])
def get_transaction(transactionId_val):
    # Return transaction by id
    if request.method == 'GET':
        return str(blockchain.getTransactionById(transactionId_val))
    
@uPCoin.route('/blockchain/transactions', methods=['GET', 'POST'])
def transaction(transactionId_val=None):
    if request.method == 'GET':
        # Return all transactions
        return str(blockchain.getAllTransactions())
    elif request.method == 'POST':
        # TODO: Test add transaction
        return str(blockchain.addTransaction(request.json))

@uPCoin.route('/blockchain/transactions/unspent/<address>', methods=['GET'])
def get_unspent_transactions(address):
    if request.method == 'GET':
        # Get all unspent transactions from the given address
        # TODO: Test
        return str(Blockchain.getUnspentTransactionsForAddress(address))

"""
Operator
"""

@uPCoin.route('/operator/wallets', methods=['GET', 'POST'])
def wallets():
    if request.method == 'GET':
        # Get all wallets
        return str(operator.getWallets())
    elif request.method == "POST":
        # Create a wallet using the specified password
        jsonData = json.loads(request.data)
        password = jsonData["password"]
        return str(operator.createWalletFromPassword(password))

@uPCoin.route('/operator/wallets/<walletId>', methods=['GET'])
def getWalletById(walletId):
    if request.method == "GET":
        # Get a wallet by the specified ID
        return str(operator.getWalletById(walletId))

@uPCoin.route('/operator/wallets/<walletId>/transactions', methods=['POST'])
def createTransaction(walletId):
    # Create a transaction
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
        transcationCreated = blockchain.addTransaction(Transaction.createTransaction(newTransaction))

        return str(transcationCreated)

@uPCoin.route('/operator/wallets/<walletId>/addresses', methods=['GET', 'POST'])
def addressesWallet(walletId):
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
        print(type(newAddress))
        return str(json.dumps({"address": newAddress}))


@uPCoin.route('/operator/wallets/<walletId>/addresses/<addressId>/balance', methods=['GET'])
def getBalance(walletId, addressId):
    if request.method == "GET":
        # Get a balance for the specified addressId and walletId
        balance = operator.getBalanceForAddress(addressId)
        return str(json.dumps({"balance": balance}))

"""
Node
"""
@uPCoin.route('/node/peers', methods=['GET', 'POST'])
def peers():
    if request.method == 'GET':
        return str(node.peers)
    elif request.method == "POST":
        jsonData = json.loads(request.data)
        newPeer = node.connectToPeer(jsonData["peer"])
        return str(newPeer)


@uPCoin.route('/node/transactions/<transactionId>/confirmations', methods=['GET'])
def getComfirmations(transactionId):
    if request.method == 'GET':
        node.getConfirmations(transactionId)

"""
Miner
"""
@uPCoin.route('/miner/mine', methods=['POST'])
def mine():
    # Mine a new block
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
