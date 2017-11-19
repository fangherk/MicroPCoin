""" Library Imports """
from flask import Flask, jsonify, request

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
    # TODO: Return block listing of all blocks and choose format
    print(type(blockchain.getAllBlocks()))
    return str(list(blockchain.getAllBlocks()))

@uPCoin.route('/blockchain/blocks/latest', methods=['GET', 'PUT'])
def latest_blocks():
    if request.method == 'GET':
        # TODO: Return latest block in ? format
        return str(blockchain.getLastBlock())
    elif request.method == 'PUT':
        # TODO: Parse the Json Put Request and add it to the blockchain
        return jsonify(request.json)

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

@uPCoin.route('/blockhain/blocks/transactions/<transactionId_val>', methods=['GET'])
def get_transaction(transactionId_val):
    # TODO: Set up Error Handling
    if request.method == 'GET':
        return blockchain.getTransactionById(transactionId_val)
    
@uPCoin.route('/blockhain/transactions', methods=['GET', 'POST'])
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
    uPCoin.run(debug=True, host='134.173.211.84')
