""" Library Imports """
from flask import Flask, jsonify, request
from flask.json import loads

import json
import Block
import Blockchain

""" --------------- """
""" --------------- """

uPCoin = Flask(__name__)
blockchain = Blockchain.Blockchain("test", "transactionsTest")

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
        output = blockchain.addBlock(blockToAdd)
        return str(output)

@uPCoin.route('/blockchain/blocks/hash/<hash_val>', methods=['GET'])
def get_block_by_hash(hash_val):
    # TODO: Set up Error Handling
    if request.method == 'GET':
        return blockchain.getBlockByHash(hash_val)

@uPCoin.route('/blockchain/blocks/index/<index_val>', methods=['GET'])
def get_block_by_index(index_val):
    # TODO: Set up Error Handling
    if request.method == 'GET':
        return blockchain.getBlockByIndex(index_val)

@uPCoin.route('/blockchain/blocks/transactions/<transactionId_val>', methods=['GET'])
def get_transaction(transactionId_val):
    # TODO: Set up Error Handling
    if request.method == 'GET':
        return blockchain.getTransactionById(transactionId_val)
    
@uPCoin.route('/blockchain/transactions', methods=['GET', 'POST'])
def transaction(transactionId_val):
    # TODO: Set up transactions for the blockchain 
    if request.method == 'GET':
        return blockchain.getAllTransactions()
    elif request.method == 'POST':
        return blockchain.addTransaction(request.json)
""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""

if __name__=='__main__':
    uPCoin.run(debug=True, host='192.168.0.200')
