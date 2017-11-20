import Wallet
import secrets
import pickle
import hashlib
import json
import binascii

class Operator:
    def __init__(self, dbName, blockChain, init=True):
        self.dbName = dbName
        self.wallets = []
        if not init:
            self.wallets = pickle.load(open(dbName, "rb"))
        else:
            pickle.dump(self.wallets, open(dbName, "wb"))
        self.blockchain = blockChain

    def __repr__(self):
        return json.dumps(self.__dict__)

    def addWallet(self, wallet):
        self.wallets.append(wallet)
        pickle.dump(self.wallets, open(self.dbName, "wb"))
        return wallet

    def createWalletFromPassword(self, password):
        hexed = hashlib.sha256(password.encode('utf-8')).hexdigest()
        wallet = Wallet.Wallet(secrets.token_hex(32), hexed)
        return self.addWallet(wallet)

    def createWalletFromHash(self, hashH):
        wallet = Wallet.Wallet(secrets.token_hex(32), hashH)
        return self.addWallet(wallet)

    def checkWalletPassword(self, walletId, hashH):
        wallet = self.getWalletById(walletId)
        if wallet == None:
            raise ValueError("Wallet Not Found")

        return wallet.passwordHash == passwordHash

    def getWallets(self):
        return self.wallets

    def getWalletById(self, walletId):
        for wallet in self.wallets:
            if wallet.id == walletId:
                return wallet

        raise ValueError("Wrong wallet id")

    def generateAddressForWallet(self, walletId):
        for idx, wallet in enumerate(self.wallets):
            if wallet.id == walletId:
                temp_wallet = wallet 
                temp_idx = idx
        if not temp_wallet and not idx: 
            address = temp_wallet.generateAddress()
            self.wallets[temp_idx] = temp_wallet
            pickle.dump(self.wallets, open(self.dbName, "wb"))
            return address
        raise ValueError("Cannot find address")


    def getAddressesForWallet(self, walletId):
        wallet = self.getWalletById(walletId)
        addresses = wallet.getAddresses()
        return addresses

    def getAddressForWallet(self, walletId, addressId):
        wallet = self.getWalletById(walletId)
        address = wallet.getAddressByPublicKey(addressId)
        return address

    def getBalanceForAddress(self, addressId):
        utxo = self.blockchain.getUnspentTransactionsForAddress(addressId)
        summed = 0
        for outputTransaction in utxo:
            summed += outputTransaction["amount"]

        return summed

    def createTransaction(self, walletId, fromAddressId, toAddressId, amount, changeAddressId):
        utxo = self.blockchain.getUnspentTransactionsForAddress(fromAddressId)
        wallet = self.getWalletById(walletId)
        secretKey = wallet.getSecretKeyByAddress(fromAddressId)

        # TODO: finish this up
        







        
