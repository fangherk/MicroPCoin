import Wallet
import TransactionBuilder
import secrets
import pickle
import hashlib
import json
import binascii

class Operator:
    def __init__(self, dbName, blockChain, init=True):
        self.dbName = dbName
        try: 
            temp_wallets = pickle.load(open(dbName, "rb"))
            self.wallets = temp_wallets
        except OSError as e:
            self.wallets = []
            pickle.dump(self.wallets, open(dbName, "wb"))
        self.blockchain = blockChain

    def __repr__(self):
        return json.dumps(self.__dict__)

    def addWallet(self, wallet):
        """ Add a wallet to all the wallets of the operator """
        self.wallets.append(wallet)
        pickle.dump(self.wallets, open(self.dbName, "wb"))
        return wallet

    def createWalletFromPassword(self, password):
        """ Create a wallet from a password """
        hexed = hashlib.sha256(password.encode('utf-8')).hexdigest()
        wallet = Wallet.Wallet(secrets.token_hex(32), hexed)
        return self.addWallet(wallet)

    def createWalletFromHash(self, hashH):
        """ Create a Wallet from the hash """
        wallet = Wallet.Wallet(secrets.token_hex(32), hashH)
        return self.addWallet(wallet)

    def checkWalletPassword(self, walletId, passwordHash):
        """ Check if a wallet exists by its password """
        wallet = self.getWalletById(walletId)
        if wallet == None:
            raise ValueError("Wallet Not Found")

        return wallet.passwordHash == passwordHash

    def getWallets(self):
        """ Return all the wallets """
        return self.wallets

    def getWalletById(self, walletId):
        """ Get the wallet by its id """
        for wallet in self.wallets:
            if wallet.id == walletId:
                return wallet

        raise ValueError("Wrong wallet id")

    def generateAddressForWallet(self, walletId):
        """ Create address for a wallet """ 
        # Finde the wallet ID in the data structure
        targetIdx = None
        for idx in range(len(self.wallets)):
            if self.wallets[idx].id == walletId:
                targetIdx = idx

        # Raise an error if not found
        if targetIdx is None:
            raise ValueError("Cannot find address")
        
        # Generate a new address
        address = self.wallets[targetIdx].generateAddress(walletId)

        # Write to the database
        pickle.dump(self.wallets, open(self.dbName, "wb"))

        # Return a generated address
        return address


    def getAddressesForWallet(self, walletId):
        """ Get addresses contained in a wallet """
        wallet = self.getWalletById(walletId)
        addresses = wallet.getAddresses()
        return addresses

    def getAddressForWallet(self, walletId, addressId):
        """ Get the address for teh wallet by the public key """
        wallet = self.getWalletById(walletId)
        address = wallet.getAddressByPublicKey(addressId)
        return address

    def getBalanceForAddress(self, addressId):
        """ Get the balance of the address """
        utxo = self.blockchain.getUnspentTransactionsForAddress(addressId)
        summed = 0
        for outputTransaction in utxo:
            summed += int(outputTransaction["amount"])

        return summed

    def createTransaction(self, walletId, fromAddressId, toAddressId, amount, changeAddressId):
        """ Create a transaction for a wallet"""

        utxo = self.blockchain.getUnspentTransactionsForAddress(fromAddressId)
        wallet = self.getWalletById(walletId)
        secretKey = wallet.getSecretKeyByAddress(fromAddressId)

        #print("utxo:{}\ntoAddressId:{}\namount:{}\nchangeAddressId:{}\nsecretKey:{}\n".format(type(utxo), type(toAddressId), type(amount), type(changeAddressId), type(secretKey)))
        #print("utxo", utxo)
        transaction = TransactionBuilder.TransactionBuilder()
        transaction.fromAddress(utxo)
        transaction.to(toAddressId, amount)
        transaction.change(changeAddressId)
        transaction.fee(1)
        transaction.sign(secretKey)
        # print(transaction)
        #print("memememememem")
        # TODO: finish this up
        return transaction.build()
        







        
