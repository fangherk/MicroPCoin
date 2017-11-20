""" Library Imports """
from flask import Flask, jsonify, request
from flask.json import loads

import json
import Block
import Blockchain
import Operator

""" --------------- """
""" --------------- """

uPCoin = Flask(__name__)
blockchain = Blockchain.Blockchain("test", "transactionsTest")
operator = Operator.Operator()

""" Main Page """
@uPCoin.route('/')
def index():
    return 'Welcome to uPCoin.'


""" Blockchain GET/POST requests """
""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""

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

""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""

@uPCoin.route('/operator/wallets', methods=['GET', 'POST'])
def wallets(passw=None):
     if request.method == 'GET':
        return operator.getWallets() 

if __name__=='__main__':
    uPCoin.run(debug=True, host='134.173.38.172')
