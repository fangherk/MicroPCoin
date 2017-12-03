""" Library Imports """
from flask import Flask, jsonify, request, render_template
from flask.json import loads, JSONEncoder

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
    # TODO: Prettify This Pag
    return render_template("upCoin.html")


""" Blockchain GET/POST requests """

@uPCoin.route('/blockchain/blocks', methods=['GET'])
def get_blocks():
    """ Return all blocks in JSON format """
    response= json.dumps(blockchain.getAllBlocks(), default = lambda o:o.__dict__)
    return response
    return render_template("response.html", response=response)

@uPCoin.route('/blockchain/blocks/latest', methods=['GET', 'PUT'])
def latest_blocks():
    """ GET: Return the latest block in JSON format
        PUT: Adda block to the blockchain """ 
    if request.method == 'GET':
        response = blockchain.getLastBlock()
        response = json.dumps(response, default = lambda o:o.__dict__)
        return response
        return render_template("response.html", response=response)
    elif request.method == 'PUT':
        # print("I get here")
        print(request.json)
        # Take in the request
        inputJSON = request.json

        # Create a block for the request
        # print("\nrequest\n", request.json)
        blockToAdd = Block.Block()
        blockToAdd.index = inputJSON["index"]
        blockToAdd.previousHash = inputJSON["previousHash"]
        blockToAdd.timestamp = inputJSON["timestamp"]
        blockToAdd.nonce = inputJSON["nonce"]
        blockToAdd.transactions = [Transaction.createTransaction(transaction) for transaction in inputJSON["transactions"]]
        # print(blockToAdd)
        blockToAdd.hash = blockToAdd.toHash()

        # Add block
        response = blockchain.addBlock(blockToAdd)
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)

@uPCoin.route('/blockchain/blocks/hash/', defaults={'hash_val':None}, methods=['GET', 'POST'])
@uPCoin.route('/blockchain/blocks/hash/<hash_val>', methods=['GET'])
def get_block_by_hash(hash_val=None):
    """ Return a block by its specified hash """
    if request.method == 'GET':
        response = blockchain.getBlockByHash(hash_val)
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)
    elif request.method == 'POST':
        hash_val = request.form["hash_val"]
        response = blockchain.getBlockByHash(hash_val)
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)


@uPCoin.route('/blockchain/blocks/index/', defaults={'index_val':None}, methods=['GET', 'POST'])
@uPCoin.route('/blockchain/blocks/index/<index_val>', methods=['GET'])
def get_block_by_index(index_val):
    """ Return a block by its specified index """
    if request.method == 'GET':
        index_val = int(index_val)
        response = blockchain.getBlockByIndex(index_val)
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)
    elif request.method == 'POST':
        index_val = int(request.form["index_val"])
        response = blockchain.getBlockByIndex(index_val)
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)



@uPCoin.route('/blockchain/blocks/transactions', defaults={'transactionId_val':None}, methods=['GET', 'POST'])
@uPCoin.route('/blockchain/blocks/transactions/<transactionId_val>', methods=['GET'])
def get_transaction(transactionId_val):
    """ Return the latest transaction by its id """
    if request.method == 'GET':
        response = blockchain.getTransactionById(transactionId_val)
        response = json.dumps(response, default = lambda o:o.__dict__)
        return response
    elif request.method == 'POST':
        transactionId_val = request.form["transactionId_val"]
        response = blockchain.getTransactionById(transactionId_val)
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)


    
@uPCoin.route('/blockchain/transactions', methods=['GET', 'POST'])
def all_transactions(transactionId_val=None):
    """ GET: Return the latest transactions
        POST: Add a transaction """
    if request.method == 'GET':
        response = blockchain.getAllTransactions()
        response = json.dumps(response, default = lambda o:o.__dict__)
        return response

    elif request.method == 'POST':
        transaction = Transaction.createTransaction(request.json)
        response = blockchain.addTransaction(transaction)
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)

@uPCoin.route('/blockchain/transactions/unspent/', defaults={'address':None}, methods=['GET', 'POST'])
@uPCoin.route('/blockchain/transactions/unspent/<address>', methods=['GET'])
def get_unspent_transactions(address):
    """ Get the unspent transactions for the address. """
    if request.method == 'GET':
        response = blockchain.getUnspentTransactionsForAddress(address)
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)
    elif request.method == 'POST':
        address = request.form["address"] 
        unspentTransaction = blockchain.getUnspentTransactionsForAddress(address)
        response = unspentTransaction
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)


"""
Operator
"""

@uPCoin.route('/operator/wallets', methods=['GET', 'POST'])
def wallets():
    """ GET: Get all wallets 
        POST: Create a new Wallet by posting a password """
    if request.method == 'GET':
        response = operator.getWallets() 
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)
    elif request.method == "POST":
        print(request)
        print("\n\n")
        print("request data", request.data)
        if request.data == b'':
            password = request.form["password"]    
        else:
            jsonData = json.loads(request.data)
            password = jsonData["password"]
        createdWallet = operator.createWalletFromPassword(password)

        # Create a wallet representation that hides the secret and passwordHash
        walletRepresentation = {}
        walletRepresentation["id"] = createdWallet.id
        walletRepresentation["keypairs"] = createdWallet.keypairs
        response = walletRepresentation
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)


@uPCoin.route('/operator/wallets/', defaults={'walletId':None}, methods=['GET', 'POST'])
@uPCoin.route('/operator/wallets/<walletId>', methods=['GET'])
def getWalletById(walletId):
    """ Get a wallet by the specified ID """
    if request.method == "GET":
        response = operator.getWalletById(walletId)
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)
    elif request.method == "POST":
        walletId = request.form["walletId"]
        response = operator.getWalletById(walletId)
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)

@uPCoin.route('/operator/wallets/<walletId>/transactions', methods=['POST'])
def createTransaction(walletId):
    """ Create a Transaction """

    if request.method == "POST":
        print(request)
        print("\n\n")
        print("request data", request.data)
        # Obtain relevant data:
        #   password, fromAddress, toAddress, amount, changeAddress
        if walletId == "Form":
            walletId = request.form["walletId"]
            password = request.form["password"]
            fromAddress = request.form["from"]
            toAddress = request.form["to"]
            amount = request.form["amount"]
            changeAddress = request.form["changeAddress"]
            if not walletId or not password or not fromAddress or not toAddress or not amount or not changeAddress: 
                return "Incorrect Input"
        else:
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
            # TODO: Change to 403 error
            return "Invalid Wallet Password. Try Again."

        # Create a transaction 
        newTransaction = operator.createTransaction(walletId, fromAddress, toAddress, amount, changeAddress)
        
        # Check if the transaction is signed correctly
        newTransaction.check()

        # Add thte transaction to the list of pending transaction
        transactionCreated = blockchain.addTransaction(Transaction.createTransactionObject(newTransaction))

        response = transactionCreated 
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)


@uPCoin.route('/operator/wallets/<walletId>/addresses', methods=['GET', 'POST'])
def addressesWallet(walletId):
    """ GET: Get all address of a wallet
        POST: Create a new address for a wallet """
    if request.method == "GET":
        # Get all addresses of a wallet
       response = operator.getAddressesForWallet(walletId)
       response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
       return render_template("response.html", response=response)
    elif request.method == "POST":
        # Create a new address

        # Obtain relevant data:
        #   password
        if walletId == "Form":
            walletId = request.form["walletId"]
            password = request.form["password"]
            print(password)
        else:
            jsonData = json.loads(request.data)
            password = jsonData["password"]

        # Compute the hash of the provided password
        passwordHash = hashlib.sha256(password.encode('utf-8')).hexdigest()

         # Check if the password hash is the same with the stored password hash
        if not operator.checkWalletPassword(walletId, passwordHash):
            # TODO: Change to 403 Error
            return "Wrong Wallet Password"

        newAddress = operator.generateAddressForWallet(walletId)
        response = json.dumps({"address": newAddress})
        return render_template("response.html", response=response)


@uPCoin.route('/operator/wallets/<walletId>/addresses/<addressId>/balance', methods=['GET', 'POST'])
def getBalance(walletId, addressId):
    """ Get the balance of a wallet """
    if request.method == "GET":
        # Get a balance for the specified addressId and walletId
        balance = operator.getBalanceForAddress(addressId)
        response = json.dumps({"balance": balance})
        return render_template("response.html", response=response)
    elif request.method == "POST":
        if walletId == "Form":
            walletId = request.form["walletId"]
            addressId = request.form["addressId"]
        balance = operator.getBalanceForAddress(addressId)
        response = json.dumps({"balance": balance})
        return render_template("response.html", response=response)




"""
Node
"""
@uPCoin.route('/node/peers', methods=['GET', 'POST'])
def peers():
    """ Find the nodes of a peer """
    if request.method == 'GET':
        response = node.peers
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)
    elif request.method == "POST":
        if request.data == b'':
            print(request.form["peer"])
            newPeer = node.connectWithPeer(request.form["peer"])
        else:
            print(request.data)
            jsonData = request.json
            newPeer = node.connectWithPeer(jsonData["peer"])
        return str(newPeer)


@uPCoin.route('/node/transactions/<transactionId>/confirmations', methods=['GET', "POST"])
def getConfirmations(transactionId):
    if request.method == 'GET':
        numConfirmations = node.getConfirmations(transactionId)
    elif request.method == 'POST':
        transactionId = request.form["transactionId"] 
        numConfirmations = node.getConfirmations(transactionId)
    response = json.dumps({"confirmations" : numConfirmations})
    return render_template("response.html", response=response)

"""
Miner
"""
@uPCoin.route('/miner/mine', methods=['POST'])
def mine():
    """ Mine a new block """ 
    if request.method == 'POST':
        # Obtain relevant data:
        #   rewardAddress

        if request.data == b'':
            rewardAddress = request.form["rewardAddress"]
        else:
            jsonData = json.loads(request.data)
            rewardAddress = jsonData["rewardAddress"]

        # Mine with the reward address
        newBlock = miner.mine(rewardAddress)

        # When this function call succeeds, it adds the block to the blockchain
        blockchain.addBlock(newBlock);

        # Output the just created block
        response = newBlock
        response = json.dumps(response, default = lambda o:o.__dict__,indent = 4, separators = (',', ': ') )
        return render_template("response.html", response=response)


if __name__=='__main__':
    uPCoin.run(threaded=True, debug=True, host=os.environ["ip"])
